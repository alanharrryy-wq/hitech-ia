from __future__ import annotations

def build_package_report(
    *,
    built_at: str,
    workspace_root: str,
    manifest_path: str,
    project_slug: str,
    package_slug: str,
    sequence: int,
    zip_name: str,
    zip_size_bytes: int,
    checksum: str,
    inventory: list[str],
    delivery: dict,
    warnings: list[str],
) -> dict:
    return {
        "schema_version": "1.0",
        "built_at": built_at,
        "workspace_root": workspace_root,
        "manifest_path": manifest_path,
        "project_slug": project_slug,
        "package_slug": package_slug,
        "sequence": sequence,
        "zip_name": zip_name,
        "zip_size_bytes": zip_size_bytes,
        "checksum": checksum,
        "inventory": inventory,
        "delivery": delivery,
        "warnings": warnings,
    }
