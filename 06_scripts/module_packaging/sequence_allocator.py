from __future__ import annotations

import re
from pathlib import Path

ZIP_PATTERN = re.compile(
    r"^zip(?P<sequence>[1-9][0-9]*)_(?P<project_slug>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package_slug>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$"
)

def next_sequence_for_project(repo_root: Path, project_slug: str) -> int:
    project_dir = repo_root / "02_modules" / "_zip_inbox" / project_slug
    if not project_dir.exists():
        return 1
    sequences: list[int] = []
    for zip_path in project_dir.glob("*.zip"):
        match = ZIP_PATTERN.fullmatch(zip_path.name)
        if match:
            sequences.append(int(match.group("sequence")))
    return max(sequences) + 1 if sequences else 1

def canonical_zip_name(sequence: int, project_slug: str, package_slug: str) -> str:
    if sequence < 1:
        raise ValueError("sequence must be >= 1")
    return f"zip{sequence}_{project_slug}_{package_slug}.zip"
