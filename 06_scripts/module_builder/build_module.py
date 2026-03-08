from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import tempfile
from pathlib import Path

from builder_report import build_builder_report
from builder_targets import validate_runtime_paths
from module_workspace_builder import build_workspace
from source_layout_validator import validate_source_layout

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def run_python(repo_root: Path, script_rel: str, *args: str) -> subprocess.CompletedProcess:
    script_path = (repo_root / script_rel).resolve()
    command = ["python", str(script_path), *args]
    return subprocess.run(command, cwd=repo_root, capture_output=True, text=True)

def build_module(*, source_root: Path, repo_root: Path, output_report: Path, project_hint: str | None = None) -> dict:
    warnings: list[str] = []
    errors: list[str] = []

    errors.extend(validate_source_layout(source_root))
    errors.extend(validate_runtime_paths(repo_root))
    if errors:
        report = build_builder_report(
            built_at=utc_now(),
            source_root=source_root.resolve().as_posix(),
            workspace_root="",
            project_slug=None,
            package_slug=None,
            package_report_path=None,
            package_zip_path=None,
            stage_outputs={},
            warnings=warnings,
            errors=errors,
        )
        write_json(output_report, report)
        return report

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        workspace_root = temp_root / "workspace"
        stage_outputs: dict = {}

        workspace_result = build_workspace(source_root, workspace_root)
        stage_outputs["workspace"] = workspace_result
        if workspace_result["collision_paths"]:
            warnings.append("workspace_path_collisions_detected")

        scan_report = temp_root / "scan_report.json"
        scan_run = run_python(repo_root, "06_scripts/module_scanner/scan_module.py", "--input", str(workspace_root), "--output", str(scan_report))
        stage_outputs["scan"] = {"returncode": scan_run.returncode, "stdout": scan_run.stdout, "stderr": scan_run.stderr}
        if scan_run.returncode != 0:
            errors.append("scanner_stage_failed")

        inference_report = temp_root / "inference_report.json"
        if not errors:
            args = ["--scan-report", str(scan_report), "--repo-root", str(repo_root), "--output", str(inference_report)]
            if project_hint:
                args.extend(["--project-hint", project_hint])
            inference_run = run_python(repo_root, "06_scripts/module_inference/infer_structure.py", *args)
            stage_outputs["inference"] = {"returncode": inference_run.returncode, "stdout": inference_run.stdout, "stderr": inference_run.stderr}
            if inference_run.returncode != 0:
                errors.append("inference_stage_failed")

        manifest_path = workspace_root / "manifest.json"
        manifest_report = temp_root / "manifest_report.json"
        if not errors:
            manifest_run = run_python(
                repo_root,
                "06_scripts/module_manifest/build_manifest.py",
                "--inference-report", str(inference_report),
                "--output-manifest", str(manifest_path),
                "--output-report", str(manifest_report),
            )
            stage_outputs["manifest"] = {"returncode": manifest_run.returncode, "stdout": manifest_run.stdout, "stderr": manifest_run.stderr}
            if manifest_run.returncode != 0:
                errors.append("manifest_stage_failed")

        package_report = temp_root / "package_report.json"
        package_zip_path = None
        project_slug = None
        package_slug = None
        if not errors:
            package_run = run_python(
                repo_root,
                "06_scripts/module_packaging/package_module.py",
                "--workspace", str(workspace_root),
                "--repo-root", str(repo_root),
                "--output-report", str(package_report),
            )
            stage_outputs["packaging"] = {"returncode": package_run.returncode, "stdout": package_run.stdout, "stderr": package_run.stderr}
            if package_run.returncode != 0:
                errors.append("packaging_stage_failed")
            else:
                package_payload = json.loads(package_report.read_text(encoding="utf-8"))
                project_slug = package_payload["project_slug"]
                package_slug = package_payload["package_slug"]
                package_zip_path = package_payload["delivery"]["final_path"]

        report = build_builder_report(
            built_at=utc_now(),
            source_root=source_root.resolve().as_posix(),
            workspace_root=workspace_root.resolve().as_posix(),
            project_slug=project_slug,
            package_slug=package_slug,
            package_report_path=package_report.resolve().as_posix() if package_report.exists() else None,
            package_zip_path=package_zip_path,
            stage_outputs=stage_outputs,
            warnings=warnings,
            errors=errors,
        )
        write_json(output_report, report)
        return report

def main() -> int:
    parser = argparse.ArgumentParser(description="Build canonical module ZIP from source folder")
    parser.add_argument("--source", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--project-hint")
    args = parser.parse_args()

    report = build_module(
        source_root=Path(args.source).resolve(),
        repo_root=Path(args.repo_root).resolve(),
        output_report=Path(args.output_report).resolve(),
        project_hint=args.project_hint,
    )

    print("STATUS:", "PASS" if report["is_valid"] else "FAIL")
    print(f"project_slug: {report['project_slug']}")
    print(f"package_slug: {report['package_slug']}")
    print(f"package_zip_path: {report['package_zip_path']}")
    return 0 if report["is_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
