from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ZIP_PATTERN = re.compile(
    r"^zip(?P<sequence>[1-9][0-9]*)_(?P<project_slug>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package_slug>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$"
)
ALLOWED_PROJECT_INTERNAL_DIRS = {"_processed", "_failed", "_staging", "_quarantine"}
ALLOWED_PROJECT_NON_ZIP_FILES = {"project.manifest.json", "project.manifest.template.json", ".gitkeep"}


@dataclass(frozen=True)
class ZipInfo:
    filename: str
    sequence: int
    project_slug: str
    package_slug: str
    relative_path: str
    sha256: str
    size_bytes: int
    modified_at_utc: str


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_from_timestamp(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_zip_name(filename: str) -> dict[str, int | str] | None:
    match = ZIP_PATTERN.fullmatch(filename)
    if not match:
        return None
    data: dict[str, int | str] = match.groupdict()
    data["sequence"] = int(data["sequence"])
    return data


def normalize(path: Path) -> str:
    return path.as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def default_arg_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", required=True, help="Repository root")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument(
        "--inbox-root",
        help="Optional inbox override; defaults to <repo-root>/02_modules/_zip_inbox",
    )
    return parser


def inbox_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "02_modules" / "_zip_inbox"


def resolve_inbox_root(repo_root: Path, inbox_override: str | None) -> Path:
    if inbox_override:
        return Path(inbox_override).resolve()
    return inbox_root_from_repo(repo_root)


def runs_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "04_runs" / "zip_inbox"


def reports_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "05_reports" / "zip_inbox"


def sequence_status_from_values(sequences: Iterable[int]) -> dict:
    values = sorted(sequences)
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    unique = sorted(counts)
    duplicates = sorted([sequence for sequence, count in counts.items() if count > 1])
    missing: list[int] = []
    if unique:
        expected = set(range(min(unique), max(unique) + 1))
        missing = sorted(expected - set(unique))
    return {
        "is_contiguous": len(duplicates) == 0 and len(missing) == 0,
        "present_sequences": unique,
        "missing_sequences": missing,
        "duplicate_sequences": duplicates,
    }


def sequence_status_from_infos(items: Iterable[ZipInfo]) -> dict:
    return sequence_status_from_values([item.sequence for item in items])


def collect_active_zip_infos(project_dir: Path, inbox_root: Path) -> list[ZipInfo]:
    items: list[ZipInfo] = []
    if not project_dir.exists() or not project_dir.is_dir():
        return items
    for file_path in sorted(project_dir.glob("*.zip"), key=lambda path: path.name.lower()):
        parsed = parse_zip_name(file_path.name)
        if not parsed:
            continue
        project_slug = str(parsed["project_slug"])
        if project_slug != project_dir.name:
            continue
        stat = file_path.stat()
        items.append(
            ZipInfo(
                filename=file_path.name,
                sequence=int(parsed["sequence"]),
                project_slug=project_slug,
                package_slug=str(parsed["package_slug"]),
                relative_path=normalize(file_path.relative_to(inbox_root)),
                sha256=sha256_file(file_path),
                size_bytes=stat.st_size,
                modified_at_utc=iso_from_timestamp(stat.st_mtime),
            )
        )
    items.sort(key=lambda item: (item.sequence, item.filename.lower()))
    return items


def collect_archived_zip_infos(project_dir: Path, inbox_root: Path, archive_folder: str) -> list[ZipInfo]:
    items: list[ZipInfo] = []
    root = project_dir / archive_folder
    if not root.exists():
        return items
    for file_path in sorted(root.rglob("*.zip"), key=lambda path: normalize(path.relative_to(project_dir))):
        parsed = parse_zip_name(file_path.name)
        if not parsed:
            continue
        project_slug = str(parsed["project_slug"])
        if project_slug != project_dir.name:
            continue
        stat = file_path.stat()
        items.append(
            ZipInfo(
                filename=file_path.name,
                sequence=int(parsed["sequence"]),
                project_slug=project_slug,
                package_slug=str(parsed["package_slug"]),
                relative_path=normalize(file_path.relative_to(inbox_root)),
                sha256=sha256_file(file_path),
                size_bytes=stat.st_size,
                modified_at_utc=iso_from_timestamp(stat.st_mtime),
            )
        )
    items.sort(key=lambda item: (item.sequence, item.relative_path.lower()))
    return items


def archive_zip(source: Path, destination: Path) -> None:
    ensure_parent(destination)
    os.replace(source, destination)


def parse_sequences(value: str | None) -> list[int]:
    if not value:
        return []
    parts = [part.strip() for part in value.split(",") if part.strip()]
    sequences = sorted({int(part) for part in parts})
    for sequence in sequences:
        if sequence < 1:
            raise ValueError(f"Sequence must be >= 1, got {sequence}")
    return sequences
