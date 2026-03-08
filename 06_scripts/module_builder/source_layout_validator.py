from __future__ import annotations

from pathlib import Path

NOISE_PARTS = {
    "__pycache__", ".pytest_cache", ".DS_Store", "Thumbs.db",
    "node_modules", "dist", "build", ".next", ".turbo", ".cache",
}

def collect_usable_files(source_root: Path) -> list[Path]:
    files = [path for path in source_root.rglob("*") if path.is_file()]
    usable: list[Path] = []
    for file_path in files:
        rel_parts = set(file_path.relative_to(source_root).parts)
        if rel_parts & NOISE_PARTS:
            continue
        if file_path.name in NOISE_PARTS:
            continue
        usable.append(file_path)
    usable.sort(key=lambda path: path.relative_to(source_root).as_posix().lower())
    return usable

def validate_source_layout(source_root: Path) -> list[str]:
    errors: list[str] = []
    if not source_root.exists():
        errors.append(f"Source path does not exist: {source_root}")
        return errors
    if not source_root.is_dir():
        errors.append(f"Source path is not a directory: {source_root}")
        return errors
    usable = collect_usable_files(source_root)
    if not usable:
        errors.append("Source folder has no usable files after noise filtering")
    return errors
