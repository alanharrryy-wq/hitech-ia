from __future__ import annotations

import subprocess
import time
from pathlib import Path

from common import TestExecutionError, ensure_parent, utc_now


def _safe_log_name(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum() or char in {"_", "-"}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("_") or "test"


def run_manifest_tests(
    tests: list[dict],
    *,
    repo_root: Path,
    logs_dir: Path,
    package_slug: str,
) -> tuple[list[dict], bool]:
    records: list[dict] = []
    required_failed = False

    logs_dir.mkdir(parents=True, exist_ok=True)

    for index, test in enumerate(tests, start=1):
        started_at = utc_now()
        started = time.perf_counter()

        name = str(test["name"])
        command = str(test["command"])
        required = bool(test.get("required", True))
        test_type = str(test.get("type", "command"))

        if test_type != "command":
            raise TestExecutionError(f"Unsupported test type: {test_type}")

        log_key = f"{index:02d}_{_safe_log_name(package_slug)}_{_safe_log_name(name)}"
        stdout_path = logs_dir / f"{log_key}.stdout.txt"
        stderr_path = logs_dir / f"{log_key}.stderr.txt"
        ensure_parent(stdout_path)
        ensure_parent(stderr_path)

        process = subprocess.run(
            command,
            cwd=repo_root,
            shell=True,
            capture_output=True,
            text=True,
        )

        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")

        finished_at = utc_now()
        duration_ms = int((time.perf_counter() - started) * 1000)

        status = "passed" if process.returncode == 0 else "failed"
        if required and process.returncode != 0:
            required_failed = True

        records.append(
            {
                "name": name,
                "type": test_type,
                "command": command,
                "started_at": started_at,
                "finished_at": finished_at,
                "exit_code": process.returncode,
                "required": required,
                "status": status,
                "duration_ms": duration_ms,
                "stdout_path": stdout_path.as_posix(),
                "stderr_path": stderr_path.as_posix(),
            }
        )

    return records, required_failed
