from __future__ import annotations

import shutil
import time
from pathlib import Path

from common import ValidationError, WiringError, resolve_repo_destination, resolve_safe_relative_path, sha256_file


def _iter_source_files(source_root: Path) -> list[Path]:
    if source_root.is_file():
        return [source_root]
    if source_root.is_dir():
        files = [path for path in source_root.rglob("*") if path.is_file()]
        files.sort(key=lambda path: path.as_posix().lower())
        return files
    return []


def build_operations(
    manifest: dict,
    *,
    extracted_root: Path,
    repo_root: Path,
    global_destinations: set[str],
) -> list[dict]:
    operations: list[dict] = []
    local_destinations: set[str] = set()
    package_slug = manifest["package_slug"]
    wiring_mode = manifest["wiring_mode"]

    targets = sorted(
        manifest.get("targets", []),
        key=lambda target: (
            str(target.get("destination", "")).lower(),
            str(target.get("source", "")).lower(),
        ),
    )

    for target in targets:
        source_rel = resolve_safe_relative_path(target["source"])
        destination_rel_root = resolve_safe_relative_path(target["destination"])
        mode = target["mode"]
        required = bool(target.get("required", True))

        source_root = (extracted_root / source_rel).resolve()
        try:
            source_root.relative_to(extracted_root)
        except ValueError as exc:
            raise WiringError(f"Source escapes extracted root: {source_rel}") from exc

        source_files = _iter_source_files(source_root)
        if not source_files:
            if required:
                raise WiringError(f"Required source not found: {source_rel}")
            continue

        if wiring_mode == "merge" and source_root.is_file():
            raise WiringError("wiring_mode=merge only supports directory sources in MVP")

        for source_file in source_files:
            if source_root.is_file():
                rel_inside = Path(source_file.name)
            else:
                rel_inside = source_file.relative_to(source_root)

            destination_candidate = (
                Path(destination_rel_root) / rel_inside.as_posix()
                if source_root.is_dir()
                else Path(destination_rel_root)
            )
            destination_abs, destination_rel = resolve_repo_destination(repo_root, destination_candidate.as_posix())

            if destination_rel in local_destinations:
                raise WiringError(f"Duplicate destination in same package: {destination_rel}")
            if destination_rel in global_destinations:
                raise WiringError(
                    f"Cross-package destination collision in same run: {destination_rel}"
                )

            local_destinations.add(destination_rel)
            operations.append(
                {
                    "package_slug": package_slug,
                    "source_abs": source_file,
                    "source_rel": source_file.relative_to(extracted_root).as_posix(),
                    "destination_abs": destination_abs,
                    "destination_rel": destination_rel,
                    "mode": mode,
                    "wiring_mode": wiring_mode,
                }
            )

    operations.sort(key=lambda op: op["destination_rel"].lower())
    return operations


def _backup_file(destination: Path, destination_rel: str, backup_root: Path) -> Path:
    backup_path = backup_root / destination_rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination, backup_path)
    return backup_path


def apply_operations(
    operations: list[dict],
    *,
    repo_root: Path,
    backup_root: Path,
) -> tuple[list[dict], list[dict], list[Path]]:
    operation_records: list[dict] = []
    backup_entries: list[dict] = []
    created_files: list[Path] = []

    backup_root.mkdir(parents=True, exist_ok=True)

    try:
        for op in operations:
            started = time.perf_counter()

            source_abs: Path = op["source_abs"]
            destination_abs: Path = op["destination_abs"]
            destination_rel: str = op["destination_rel"]
            mode: str = op["mode"]
            wiring_mode: str = op["wiring_mode"]

            if not source_abs.exists() or not source_abs.is_file():
                raise WiringError(f"Source file missing at apply time: {op['source_rel']}")

            destination_exists = destination_abs.exists()
            checksum_before = sha256_file(destination_abs) if destination_exists and destination_abs.is_file() else None
            source_checksum = sha256_file(source_abs)

            result = "applied"
            action = "copy"
            bytes_written = 0

            if destination_exists:
                if destination_abs.is_dir():
                    raise WiringError(f"Destination is a directory, expected file: {destination_rel}")
                if mode in {"create_only", "fail_if_exists"}:
                    raise WiringError(f"Destination already exists and mode blocks overwrite: {destination_rel}")
                if mode == "skip_if_exists":
                    result = "skipped_existing"
                    bytes_written = 0
                    checksum_after = checksum_before
                    duration_ms = int((time.perf_counter() - started) * 1000)
                    operation_records.append(
                        {
                            "package_slug": op["package_slug"],
                            "source": op["source_rel"],
                            "destination": destination_rel,
                            "action": action,
                            "result": result,
                            "duration_ms": duration_ms,
                            "bytes_written": bytes_written,
                            "checksum_before": checksum_before,
                            "checksum_after": checksum_after,
                        }
                    )
                    continue
                if wiring_mode == "merge":
                    if checksum_before == source_checksum:
                        result = "merged_same"
                        bytes_written = 0
                        checksum_after = checksum_before
                        duration_ms = int((time.perf_counter() - started) * 1000)
                        operation_records.append(
                            {
                                "package_slug": op["package_slug"],
                                "source": op["source_rel"],
                                "destination": destination_rel,
                                "action": "merge",
                                "result": result,
                                "duration_ms": duration_ms,
                                "bytes_written": bytes_written,
                                "checksum_before": checksum_before,
                                "checksum_after": checksum_after,
                            }
                        )
                        continue
                    raise WiringError(f"Guarded merge conflict at destination: {destination_rel}")

                backup_path = _backup_file(destination_abs, destination_rel, backup_root)
                backup_entries.append(
                    {
                        "destination": destination_abs,
                        "destination_rel": destination_rel,
                        "backup": backup_path,
                    }
                )

            destination_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_abs, destination_abs)
            if not destination_exists:
                created_files.append(destination_abs)

            bytes_written = destination_abs.stat().st_size
            checksum_after = sha256_file(destination_abs)
            duration_ms = int((time.perf_counter() - started) * 1000)

            operation_records.append(
                {
                    "package_slug": op["package_slug"],
                    "source": op["source_rel"],
                    "destination": destination_rel,
                    "action": "merge" if wiring_mode == "merge" else action,
                    "result": result,
                    "duration_ms": duration_ms,
                    "bytes_written": bytes_written,
                    "checksum_before": checksum_before,
                    "checksum_after": checksum_after,
                }
            )
    except Exception as exc:  # noqa: BLE001
        error = WiringError(str(exc))
        setattr(error, "operation_records", operation_records)
        setattr(error, "backup_entries", backup_entries)
        setattr(error, "created_files", created_files)
        raise error from exc

    return operation_records, backup_entries, created_files


def rollback_package_changes(
    *,
    backups: list[dict],
    created_files: list[Path],
) -> list[str]:
    messages: list[str] = []

    for created in sorted(created_files, key=lambda path: path.as_posix().lower(), reverse=True):
        if created.exists():
            created.unlink()
            messages.append(f"Deleted created file: {created}")

    for backup in reversed(backups):
        destination: Path = backup["destination"]
        backup_path: Path = backup["backup"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, destination)
        messages.append(f"Restored backup: {destination}")

    return messages
