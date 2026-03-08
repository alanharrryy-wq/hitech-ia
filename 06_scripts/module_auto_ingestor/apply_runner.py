from __future__ import annotations

import subprocess
from pathlib import Path


def run_project_pipeline(
    *,
    repo_root: Path,
    project_slug: str,
    mode: str = "dry_run",
    run_id: str | None = None,
) -> dict:
    if mode not in {"dry_run", "apply"}:
        raise ValueError(f"Unsupported mode: {mode}")

    command = [
        "python",
        str((repo_root / "run_full_cycle.py").resolve()),
        "--project",
        project_slug,
        "--repo-root",
        str(repo_root.resolve()),
        "--mode",
        mode,
    ]
    if run_id:
        command.extend(["--run-id", run_id])

    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True)
    return {
        "project_slug": project_slug,
        "mode": mode,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "status": "success" if completed.returncode == 0 else "failed",
    }
