from __future__ import annotations

def build_generation_report(
    *,
    built_at: str,
    spec_path: str,
    workspace_root: str,
    normalized_spec: dict,
    created_files: list[str],
    builder_report_path: str | None,
    builder_package_zip_path: str | None,
    warnings: list[str],
    errors: list[str],
) -> dict:
    return {
        "schema_version": "1.0",
        "built_at": built_at,
        "spec_path": spec_path,
        "workspace_root": workspace_root,
        "normalized_spec": normalized_spec,
        "created_files": created_files,
        "builder_report_path": builder_report_path,
        "builder_package_zip_path": builder_package_zip_path,
        "warnings": warnings,
        "errors": errors,
        "is_valid": len(errors) == 0,
    }
