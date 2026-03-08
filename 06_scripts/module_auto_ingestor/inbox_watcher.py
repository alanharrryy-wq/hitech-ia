from __future__ import annotations

import time
from pathlib import Path

from project_queue import build_project_queue


def watch_project_queue(
    *,
    repo_root: Path,
    project_filter: str | None = None,
    interval_sec: int = 15,
    max_loops: int = 1,
):
    loops = 0
    while True:
        yield build_project_queue(repo_root, project_filter=project_filter)
        loops += 1
        if max_loops and loops >= max_loops:
            return
        time.sleep(interval_sec)
