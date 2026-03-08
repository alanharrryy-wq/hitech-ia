from __future__ import annotations

import shutil
import zipfile
from pathlib import Path, PurePosixPath

from common import ExtractionSafetyError, ValidationError, resolve_safe_relative_path


def _validate_zip_member(member_name: str) -> str:
    try:
        safe_rel = resolve_safe_relative_path(member_name)
    except ValidationError as exc:
        raise ExtractionSafetyError(str(exc)) from exc
    pure = PurePosixPath(safe_rel)
    if any(part == ".." for part in pure.parts):
        raise ExtractionSafetyError(f"Unsafe ZIP entry contains traversal: {member_name}")
    return str(pure)


def inspect_zip_paths(zip_path: Path) -> tuple[list[str], list[str]]:
    safe_entries: list[str] = []
    errors: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename.lower()):
            name = info.filename.replace("\\", "/")
            if not name or name.endswith("/"):
                continue
            try:
                safe_entries.append(_validate_zip_member(name))
            except ExtractionSafetyError as exc:
                errors.append(str(exc))
    return safe_entries, errors


def extract_zip_safely(zip_path: Path, destination: Path) -> list[Path]:
    safe_entries, errors = inspect_zip_paths(zip_path)
    if errors:
        raise ExtractionSafetyError("; ".join(errors))

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    extracted_files: list[Path] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        for rel_path in safe_entries:
            info = archive.getinfo(rel_path)
            target = destination / PurePosixPath(rel_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, target.open("wb") as output:
                output.write(source.read())
            extracted_files.append(target)

    extracted_files.sort(key=lambda path: path.as_posix().lower())
    return extracted_files
