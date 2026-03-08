from __future__ import annotations

def build_inference_report(
    *,
    scan_report_path: str,
    scan_report: dict,
    project_resolution: dict,
    probable_package_slug: str,
    target_suggestions: list[dict],
    dependency_hints: list[dict],
    warnings: list[str],
    inferred_at: str,
) -> dict:
    return {
        "schema_version": "1.0",
        "inferred_at": inferred_at,
        "scan_report_path": scan_report_path,
        "probable_project_slug": project_resolution["probable_project_slug"],
        "project_resolution": project_resolution,
        "probable_package_slug": probable_package_slug,
        "target_suggestions": target_suggestions,
        "dependency_hints": dependency_hints,
        "signals_snapshot": scan_report.get("signals", {}),
        "warnings": sorted(set(warnings)),
    }
