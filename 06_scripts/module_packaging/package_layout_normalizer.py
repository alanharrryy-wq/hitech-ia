from __future__ import annotations

from pathlib import Path

EXCLUDED_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "Thumbs.db",
}

def iter_workspace_files(workspace_root: Path) -> list[Path]:
    files = [path for path in workspace_root.rglob("*") if path.is_file()]
    filtered: list[Path] = []
    for file_path in files:
        rel_parts = set(file_path.relative_to(workspace_root).parts)
        if rel_parts & EXCLUDED_NAMES:
            continue
        if file_path.name in EXCLUDED_NAMES:
            continue
        filtered.append(file_path)
    filtered.sort(key=lambda path: path.relative_to(workspace_root).as_posix().lower())
    return filtered

def validate_workspace(workspace_root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = workspace_root / "manifest.json"
    if not workspace_root.exists() or not workspace_root.is_dir():
        errors.append(f"Workspace does not exist or is not a directory: {workspace_root}")
        return errors
    if not manifest_path.exists():
        errors.append("Workspace missing manifest.json")
    return errors
