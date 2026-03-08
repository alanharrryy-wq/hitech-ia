from __future__ import annotations

import json
import zipfile
from pathlib import Path


def create_repo_layout(repo_root: Path, project_slug: str = "sample_project") -> Path:
    for relative in [
        "02_modules/_zip_inbox",
        "02_modules/_zip_archive",
        "02_modules/_zip_quarantine",
        "04_runs/zip_inbox",
        "05_reports/zip_inbox",
    ]:
        (repo_root / relative).mkdir(parents=True, exist_ok=True)

    project_dir = repo_root / "02_modules" / "_zip_inbox" / project_slug
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def default_manifest(
    *,
    project_slug: str,
    package_slug: str,
    sequence: int,
    target_source: str,
    target_destination: str,
    test_command: str = "python -c \"print('ok')\"",
) -> dict:
    return {
        "schema_version": "1.0",
        "project_slug": project_slug,
        "package_slug": package_slug,
        "sequence": sequence,
        "package_version": "0.1.0",
        "kind": "module",
        "wiring_mode": "copy",
        "targets": [
            {
                "source": target_source,
                "destination": target_destination,
                "mode": "overwrite",
                "required": True,
            }
        ],
        "tests": [
            {
                "name": f"smoke_{package_slug}",
                "type": "command",
                "command": test_command,
                "required": True,
            }
        ],
    }


def create_zip_artifact(
    *,
    project_dir: Path,
    project_slug: str,
    package_slug: str,
    sequence: int,
    manifest: dict,
    file_map: dict[str, str] | None = None,
    unsafe_entries: dict[str, str] | None = None,
) -> Path:
    zip_name = f"zip{sequence}_{project_slug}_{package_slug}.zip"
    zip_path = project_dir / zip_name

    payload_files = file_map or {"payload/content.txt": f"content-{package_slug}\n"}

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        for relative, content in payload_files.items():
            archive.writestr(relative, content)
        for relative, content in (unsafe_entries or {}).items():
            archive.writestr(relative, content)

    return zip_path
