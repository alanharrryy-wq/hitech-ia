from __future__ import annotations

import datetime as dt
from pathlib import Path

from common import (
    archive_root_from_repo,
    date_partition_path,
    move_with_conflict_check,
    quarantine_root_from_repo,
    sha256_file,
    utc_now,
)


def move_processed_zip(
    *,
    repo_root: Path,
    project_slug: str,
    source_zip: Path,
    run_id: str,
    when: dt.datetime,
) -> dict:
    archive_root = archive_root_from_repo(repo_root)
    destination_dir = date_partition_path(archive_root, project_slug, when)
    destination = destination_dir / source_zip.name
    result = move_with_conflict_check(source_zip, destination)
    return {
        "original_path": source_zip.as_posix(),
        "final_path": destination.as_posix(),
        "moved_at": utc_now(),
        "checksum": sha256_file(destination),
        "run_id": run_id,
        "result": result,
    }


def move_quarantine_zip(
    *,
    repo_root: Path,
    project_slug: str,
    source_zip: Path,
    run_id: str,
    reason: str,
    when: dt.datetime,
) -> dict:
    quarantine_root = quarantine_root_from_repo(repo_root)
    destination_dir = date_partition_path(quarantine_root, project_slug, when)
    destination = destination_dir / source_zip.name
    result = move_with_conflict_check(source_zip, destination)
    return {
        "original_path": source_zip.as_posix(),
        "final_path": destination.as_posix(),
        "moved_at": utc_now(),
        "checksum": sha256_file(destination),
        "run_id": run_id,
        "reason": reason,
        "result": result,
    }
