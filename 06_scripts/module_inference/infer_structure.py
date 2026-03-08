from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path, PurePosixPath

from dependency_hints import infer_dependency_hints
from inference_report import build_inference_report
from package_slug_inference import infer_package_slug
from project_slug_resolver import resolve_project_slug, slugify
from target_inference import infer_target_suggestions

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def derive_source_slug(scan_report: dict) -> str:
    input_path = str(scan_report.get("input_path", ""))
    name = PurePosixPath(input_path).stem if input_path else "new_project"
    signals = scan_report.get("signals", {})
    if signals.get("probable_primary_language") and name in {"module", "source", "input", "raw"}:
        name = f"{signals['probable_primary_language']}_module"
    return slugify(name)

def infer_structure(*, scan_report: dict, repo_root: Path, scan_report_path: str, project_hint: str | None = None) -> dict:
    warnings: list[str] = []
    source_slug = derive_source_slug(scan_report)

    project_resolution_obj = resolve_project_slug(
        repo_root=repo_root,
        source_slug=source_slug,
        explicit_hint=project_hint,
    )
    project_resolution = {
        "probable_project_slug": project_resolution_obj.probable_project_slug,
        "resolution_mode": project_resolution_obj.resolution_mode,
        "confidence": project_resolution_obj.confidence,
        "tentative_sequence": project_resolution_obj.tentative_sequence,
        "candidates": project_resolution_obj.candidates,
        "warnings": project_resolution_obj.warnings,
    }
    warnings.extend(project_resolution_obj.warnings)

    probable_package_slug, package_warnings = infer_package_slug(scan_report)
    warnings.extend(package_warnings)

    target_suggestions = infer_target_suggestions(scan_report)
    dependency_hints = infer_dependency_hints(scan_report)

    if not target_suggestions:
        warnings.append("No target suggestions generated from scan report")

    return build_inference_report(
        scan_report_path=scan_report_path,
        scan_report=scan_report,
        project_resolution=project_resolution,
        probable_package_slug=probable_package_slug,
        target_suggestions=target_suggestions,
        dependency_hints=dependency_hints,
        warnings=warnings,
        inferred_at=utc_now(),
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Infer project/package/targets from scan report")
    parser.add_argument("--scan-report", required=True, help="Path to scan_report.json")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--project-hint", help="Optional project slug hint")
    parser.add_argument("--output", required=True, help="Output path for inference report")
    args = parser.parse_args()

    scan_report_path = Path(args.scan_report).resolve()
    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output)

    scan_report = json.loads(scan_report_path.read_text(encoding="utf-8"))
    report = infer_structure(
        scan_report=scan_report,
        repo_root=repo_root,
        scan_report_path=scan_report_path.as_posix(),
        project_hint=args.project_hint,
    )
    write_json(output_path, report)

    print("STATUS: PASS")
    print(f"project_slug: {report['probable_project_slug']}")
    print(f"project_mode: {report['project_resolution']['resolution_mode']}")
    print(f"package_slug: {report['probable_package_slug']}")
    print(f"target_count: {len(report['target_suggestions'])}")
    print(f"report_path: {output_path.resolve().as_posix()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
