from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def deliver_zip(*, zip_path: Path, repo_root: Path, project_slug: str) -> dict:
    inbox_dir = repo_root / "02_modules" / "_zip_inbox" / project_slug
    inbox_dir.mkdir(parents=True, exist_ok=True)

    destination = inbox_dir / zip_path.name
    source_checksum = sha256_file(zip_path)

    if destination.exists():
        destination_checksum = sha256_file(destination)
        if destination_checksum == source_checksum:
            zip_path.unlink()
            return {
                "delivery_result": "deduplicated",
                "final_path": destination.resolve().as_posix(),
                "checksum": source_checksum,
            }
        raise ValueError(f"Conflicting ZIP already exists at destination: {destination}")

    shutil.move(str(zip_path), str(destination))
    return {
        "delivery_result": "moved",
        "final_path": destination.resolve().as_posix(),
        "checksum": source_checksum,
    }
