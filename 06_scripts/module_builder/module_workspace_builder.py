from __future__ import annotations

import shutil
from pathlib import Path

from source_layout_validator import collect_usable_files

def _destination_for_source(rel_path: Path) -> Path:
    rel_str = rel_path.as_posix().lower()
    parts = [part.lower() for part in rel_path.parts]
    if "src" in parts:
        idx = parts.index("src")
        suffix = Path(*rel_path.parts[idx + 1 :])
        return Path("src") / suffix if suffix.parts else Path("src")
    if "tests" in parts:
        idx = parts.index("tests")
        suffix = Path(*rel_path.parts[idx + 1 :])
        return Path("tests") / suffix if suffix.parts else Path("tests")
    if "test" in parts:
        idx = parts.index("test")
        suffix = Path(*rel_path.parts[idx + 1 :])
        return Path("tests") / suffix if suffix.parts else Path("tests")
    if "docs" in parts or rel_str.endswith(".md") or rel_str.endswith(".rst"):
        if "docs" in parts:
            idx = parts.index("docs")
            suffix = Path(*rel_path.parts[idx + 1 :])
            return Path("docs") / suffix if suffix.parts else Path("docs")
        return Path("docs") / rel_path.name
    if rel_path.suffix.lower() in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return Path("config") / rel_path.name
    return Path("assets") / rel_path

def build_workspace(source_root: Path, workspace_root: Path) -> dict:
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    collisions: list[str] = []

    seen_destinations: set[str] = set()
    for source_file in collect_usable_files(source_root):
        rel = source_file.relative_to(source_root)
        destination_rel = _destination_for_source(rel).as_posix()
        if destination_rel in seen_destinations:
            collisions.append(destination_rel)
            continue
        seen_destinations.add(destination_rel)
        destination = workspace_root / destination_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)
        copied.append(destination_rel)

    copied.sort(key=str.lower)
    collisions.sort(key=str.lower)
    return {
        "workspace_root": workspace_root.resolve().as_posix(),
        "copied_files": copied,
        "collision_paths": collisions,
    }
