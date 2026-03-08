from __future__ import annotations

def build_builder_report(
    *,
    built_at: str,
    source_root: str,
    workspace_root: str,
    project_slug: str | None,
    package_slug: str | None,
    package_report_path: str | None,
    package_zip_path: str | None,
    stage_outputs: dict,
    warnings: list[str],
    errors: list[str],
) -> dict:
    return {
        "schema_version": "1.0",
        "built_at": built_at,
        "source_root": source_root,
        "workspace_root": workspace_root,
        "project_slug": project_slug,
        "package_slug": package_slug,
        "package_report_path": package_report_path,
        "package_zip_path": package_zip_path,
        "stage_outputs": stage_outputs,
        "warnings": warnings,
        "errors": errors,
        "is_valid": len(errors) == 0,
    }
