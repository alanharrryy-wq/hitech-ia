from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

ZIP_PATTERN = re.compile(
    r"^zip(?P<sequence>[1-9][0-9]*)_(?P<project_slug>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package_slug>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$"
)

MANIFEST_CANDIDATE_PATHS = ("manifest.json", ".hitech/manifest.json")
SUPPORTED_WIRING_MODES = {"copy", "merge"}
SUPPORTED_TARGET_MODES = {"overwrite", "create_only", "skip_if_exists", "fail_if_exists"}
SUPPORTED_TEST_TYPES = {"command"}

ALLOWED_PROJECT_INTERNAL_DIRS = {"_processed", "_failed", "_staging", "_quarantine"}
ALLOWED_PROJECT_NON_ZIP_FILES = {"project.manifest.json", "project.manifest.template.json", ".gitkeep"}

FORBIDDEN_DEST_PREFIXES = {
    ".git",
    "02_modules/_zip_inbox",
    "02_modules/_zip_archive",
    "02_modules/_zip_quarantine",
    "04_runs",
    "05_reports",
}


class ZipInboxError(RuntimeError):
    pass


class ValidationError(ZipInboxError):
    pass


class LockError(ZipInboxError):
    pass


class ExtractionSafetyError(ZipInboxError):
    pass


class WiringError(ZipInboxError):
    pass


class TestExecutionError(ZipInboxError):
    pass


class ArchiveError(ZipInboxError):
    pass


@dataclass(frozen=True)
class ZipArtifact:
    filename: str
    sequence: int
    project_slug: str
    package_slug: str
    path: Path
    relative_path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class PackageIdentity:
    sequence: int
    project_slug: str
    package_slug: str


@dataclass(frozen=True)
class RunContext:
    repo_root: Path
    project_slug: str
    run_id: str
    started_at: str
    runs_dir: Path
    staging_dir: Path
    logs_dir: Path
    backups_dir: Path
    report_dir: Path


def utc_datetime_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def utc_now() -> str:
    return utc_datetime_now().isoformat().replace("+00:00", "Z")


def format_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id_for_project(project_slug: str, when: dt.datetime | None = None) -> str:
    now = when or utc_datetime_now()
    return now.strftime("%Y%m%dT%H%M%SZ") + "_" + project_slug


def iso_date_parts(value: dt.datetime | None = None) -> tuple[str, str, str]:
    now = (value or utc_datetime_now()).astimezone(dt.timezone.utc)
    return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(path: Path) -> str:
    return path.as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_zip_name(filename: str) -> PackageIdentity | None:
    match = ZIP_PATTERN.fullmatch(filename)
    if not match:
        return None
    return PackageIdentity(
        sequence=int(match.group("sequence")),
        project_slug=match.group("project_slug"),
        package_slug=match.group("package_slug"),
    )


def sequence_status_from_values(sequences: Iterable[int]) -> dict:
    values = sorted(sequences)
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1

    present = sorted(counts)
    duplicates = sorted([value for value, count in counts.items() if count > 1])
    missing: list[int] = []
    if present:
        expected = set(range(min(present), max(present) + 1))
        missing = sorted(expected - set(present))

    return {
        "is_contiguous": len(duplicates) == 0 and len(missing) == 0,
        "present_sequences": present,
        "missing_sequences": missing,
        "duplicate_sequences": duplicates,
    }


def default_arg_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", default=".", help="Repository root (default: current dir)")
    parser.add_argument("--inbox-root", help="Optional inbox root override")
    return parser


def repo_root_from_arg(repo_root: str) -> Path:
    return Path(repo_root).resolve()


def inbox_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "02_modules" / "_zip_inbox"


def archive_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "02_modules" / "_zip_archive"


def quarantine_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "02_modules" / "_zip_quarantine"


def runs_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "04_runs" / "zip_inbox"


def reports_root_from_repo(repo_root: Path) -> Path:
    return repo_root / "05_reports" / "zip_inbox"


def resolve_inbox_root(repo_root: Path, inbox_override: str | None) -> Path:
    if inbox_override:
        return Path(inbox_override).resolve()
    return inbox_root_from_repo(repo_root)


def resolve_safe_relative_path(path_value: str) -> str:
    if not isinstance(path_value, str) or not path_value.strip():
        raise ValidationError("Path must be a non-empty string")

    candidate = path_value.replace("\\", "/").strip()
    if "\x00" in candidate:
        raise ValidationError(f"Path contains null byte: {path_value}")

    if re.match(r"^[a-zA-Z]:", candidate):
        raise ValidationError(f"Absolute drive path is not allowed: {path_value}")
    if candidate.startswith("/"):
        raise ValidationError(f"Absolute path is not allowed: {path_value}")

    pure = PurePosixPath(candidate)
    if pure.is_absolute():
        raise ValidationError(f"Absolute path is not allowed: {path_value}")

    for part in pure.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            raise ValidationError(f"Path traversal is not allowed: {path_value}")

    normalized = str(pure).replace("\\", "/")
    if normalized.startswith("../") or normalized == "..":
        raise ValidationError(f"Path traversal is not allowed: {path_value}")
    return normalized


def resolve_repo_destination(repo_root: Path, destination: str) -> tuple[Path, str]:
    safe_rel = resolve_safe_relative_path(destination)

    for forbidden_prefix in FORBIDDEN_DEST_PREFIXES:
        if safe_rel == forbidden_prefix or safe_rel.startswith(forbidden_prefix + "/"):
            raise ValidationError(f"Destination not allowed by policy: {safe_rel}")

    resolved = (repo_root / safe_rel).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ValidationError(f"Destination escapes repo root: {safe_rel}") from exc

    return resolved, safe_rel


def collect_project_dirs(inbox_root: Path, project_slug: str | None = None) -> list[Path]:
    if not inbox_root.exists() or not inbox_root.is_dir():
        return []

    project_dirs = []
    for child in sorted(inbox_root.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        if project_slug and child.name != project_slug:
            continue
        project_dirs.append(child)
    return project_dirs


def collect_active_zip_artifacts(project_dir: Path, inbox_root: Path) -> list[ZipArtifact]:
    artifacts: list[ZipArtifact] = []
    if not project_dir.exists() or not project_dir.is_dir():
        return artifacts

    for zip_path in sorted(project_dir.glob("*.zip"), key=lambda item: item.name.lower()):
        parsed = parse_zip_name(zip_path.name)
        if not parsed:
            continue
        if parsed.project_slug != project_dir.name:
            continue
        artifacts.append(
            ZipArtifact(
                filename=zip_path.name,
                sequence=parsed.sequence,
                project_slug=parsed.project_slug,
                package_slug=parsed.package_slug,
                path=zip_path,
                relative_path=normalize(zip_path.relative_to(inbox_root)),
                sha256=sha256_file(zip_path),
                size_bytes=zip_path.stat().st_size,
            )
        )

    artifacts.sort(key=lambda item: (item.sequence, item.filename.lower()))
    return artifacts


def date_partition_path(base_root: Path, project_slug: str, when: dt.datetime | None = None) -> Path:
    year, month, day = iso_date_parts(when)
    return base_root / project_slug / year / month / day


def move_with_conflict_check(source: Path, destination: Path) -> str:
    ensure_parent(destination)
    if destination.exists():
        source_hash = sha256_file(source)
        destination_hash = sha256_file(destination)
        if source_hash == destination_hash:
            source.unlink()
            return "deduplicated"
        raise ArchiveError(f"Archive/quarantine destination conflict with different checksum: {destination}")

    os.replace(source, destination)
    return "moved"


def manifest_candidate_paths() -> tuple[str, ...]:
    return MANIFEST_CANDIDATE_PATHS


def parse_sequences(value: str | None) -> list[int]:
    if not value:
        return []
    values = sorted({int(part.strip()) for part in value.split(",") if part.strip()})
    for number in values:
        if number < 1:
            raise ValidationError(f"Sequence must be >= 1, got {number}")
    return values


def summarize_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error}"
