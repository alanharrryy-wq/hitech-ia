from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import tempfile
from pathlib import Path

from generation_report import build_generation_report
from module_autodocs import write_docs
from module_autotests import write_tests
from module_skeleton import build_workspace_skeleton
from spec_parser import load_and_normalize_spec

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def seed_manifest(spec: dict, workspace_root: Path) -> str:
    manifest = {
        "schema_version": "1.0",
        "project_slug": spec["project_slug"],
        "package_slug": spec["package_slug"],
        "sequence": 1,
        "package_version": "0.1.0",
        "kind": "module",
        "wiring_mode": "copy",
        "targets": [],
        "tests": [],
        "depends_on": [],
        "notes": spec["summary"],
    }
    path = workspace_root / "manifest.seed.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "manifest.seed.json"

def run_builder(repo_root: Path, source_root: Path, output_report: Path, project_hint: str | None) -> subprocess.CompletedProcess:
    command = [
        "python",
        str((repo_root / "06_scripts" / "module_builder" / "build_module.py").resolve()),
        "--source", str(source_root),
        "--repo-root", str(repo_root),
        "--output-report", str(output_report),
    ]
    if project_hint:
        command.extend(["--project-hint", project_hint])
    return subprocess.run(command, cwd=repo_root, capture_output=True, text=True)

def generate_module(*, spec_path: Path, repo_root: Path, output_report: Path) -> dict:
    warnings: list[str] = []
    errors: list[str] = []

    normalized_spec, parser_warnings = load_and_normalize_spec(spec_path)
    warnings.extend(parser_warnings)

    builder_script = repo_root / "06_scripts" / "module_builder" / "build_module.py"
    if not builder_script.exists():
        errors.append(f"Missing builder runtime: {builder_script}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        workspace_root = temp_root / "generated_workspace"
        created_files: list[str] = []

        if not errors:
            skeleton = build_workspace_skeleton(normalized_spec, workspace_root)
            created_files.extend(skeleton["created"])
            created_files.extend(write_docs(normalized_spec, workspace_root))
            created_files.extend(write_tests(normalized_spec, workspace_root))
            created_files.append(seed_manifest(normalized_spec, workspace_root))
            created_files = sorted(set(created_files), key=str.lower)

        builder_report_path = temp_root / "builder_report.json"
        builder_package_zip_path = None

        if not errors:
            completed = run_builder(
                repo_root=repo_root,
                source_root=workspace_root,
                output_report=builder_report_path,
                project_hint=normalized_spec.get("project_hint") or normalized_spec["project_slug"],
            )
            if completed.returncode != 0:
                errors.append("builder_stage_failed")
                if completed.stdout.strip():
                    warnings.append(completed.stdout.strip())
                if completed.stderr.strip():
                    warnings.append(completed.stderr.strip())
            elif builder_report_path.exists():
                payload = json.loads(builder_report_path.read_text(encoding="utf-8"))
                builder_package_zip_path = payload.get("package_zip_path")

        report = build_generation_report(
            built_at=utc_now(),
            spec_path=spec_path.resolve().as_posix(),
            workspace_root=workspace_root.resolve().as_posix(),
            normalized_spec=normalized_spec,
            created_files=created_files,
            builder_report_path=builder_report_path.resolve().as_posix() if builder_report_path.exists() else None,
            builder_package_zip_path=builder_package_zip_path,
            warnings=warnings,
            errors=errors,
        )
        write_json(output_report, report)
        return report

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate module workspace from spec and hand off to builder")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-report", required=True)
    args = parser.parse_args()

    report = generate_module(
        spec_path=Path(args.spec).resolve(),
        repo_root=Path(args.repo_root).resolve(),
        output_report=Path(args.output_report).resolve(),
    )
    print("STATUS:", "PASS" if report["is_valid"] else "FAIL")
    print(f"workspace_root: {report['workspace_root']}")
    print(f"builder_package_zip_path: {report['builder_package_zip_path']}")
    return 0 if report["is_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
