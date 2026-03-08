from __future__ import annotations

import json
import os
from pathlib import Path

from common import LockError, ensure_parent, utc_now


class InstallLock:
    def __init__(self, repo_root: Path, run_id: str, project_slug: str, lock_name: str = ".install.lock") -> None:
        self.repo_root = repo_root
        self.run_id = run_id
        self.project_slug = project_slug
        self.lock_path = repo_root / lock_name
        self._fd: int | None = None

    def acquire(self) -> None:
        ensure_parent(self.lock_path)
        payload = {
            "run_id": self.run_id,
            "project_slug": self.project_slug,
            "pid": os.getpid(),
            "acquired_at": utc_now(),
        }

        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            self._fd = os.open(str(self.lock_path), flags)
            os.write(self._fd, json.dumps(payload, indent=2).encode("utf-8"))
        except FileExistsError as exc:
            raise LockError(f"Another install appears to be active: {self.lock_path}") from exc
        except OSError as exc:
            raise LockError(f"Failed to acquire lock {self.lock_path}: {exc}") from exc

    def release(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

        if self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except OSError as exc:
                raise LockError(f"Failed to release lock {self.lock_path}: {exc}") from exc

    def __enter__(self) -> "InstallLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
