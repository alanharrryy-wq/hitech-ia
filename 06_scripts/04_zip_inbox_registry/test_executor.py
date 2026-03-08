from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from command_policy import resolve_test_cwd
from common import TestExecutionError, ensure_parent, utc_now


TIMEOUT_EXIT_CODE = 124


def _safe_log_name(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum() or char in {"_", "-"}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("_") or "test"


def _build_runtime_env(overrides: dict[str, str]) -> dict[str, str]:
    env = dict(os.environ)
    env.update(overrides)
    return env


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
        required = bool(test.get("required", True))
        test_type = str(test.get("type", "command"))
        args = list(test.get("args", []))
        command = str(test.get("command", ""))
        cwd_rel = str(test.get("cwd", "."))
        timeout_sec = int(test.get("timeout_sec", 300))
        env_overrides = dict(test.get("env", {}))

        if test_type != "command":
            raise TestExecutionError(f"Unsupported test type: {test_type}")
        if not args:
            raise TestExecutionError(f"Command args missing for test: {name}")

        log_key = f"{index:02d}_{_safe_log_name(package_slug)}_{_safe_log_name(name)}"
        stdout_path = logs_dir / f"{log_key}.stdout.txt"
        stderr_path = logs_dir / f"{log_key}.stderr.txt"
        ensure_parent(stdout_path)
        ensure_parent(stderr_path)

        try:
            cwd_abs = resolve_test_cwd(repo_root, cwd_rel)
        except Exception as exc:  # noqa: BLE001
            raise TestExecutionError(f"Invalid cwd for test {name}: {exc}") from exc

        status = "passed"
        exit_code = 0
        stdout_text = ""
        stderr_text = ""

        try:
            process = subprocess.run(
                args,
                cwd=cwd_abs,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=_build_runtime_env(env_overrides),
            )
            exit_code = process.returncode
            stdout_text = process.stdout
            stderr_text = process.stderr
            status = "passed" if process.returncode == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            status = "failed"
            exit_code = TIMEOUT_EXIT_CODE
            stdout_text = exc.stdout or ""
            stderr_text = (exc.stderr or "") + f"\\nTIMEOUT: command exceeded {timeout_sec} seconds\\n"

        stdout_path.write_text(stdout_text, encoding="utf-8")
        stderr_path.write_text(stderr_text, encoding="utf-8")

        finished_at = utc_now()
        duration_ms = int((time.perf_counter() - started) * 1000)

        if required and exit_code != 0:
            required_failed = True

        records.append(
            {
                "name": name,
                "type": test_type,
                "command": command,
                "args": args,
                "cwd": cwd_rel,
                "timeout_sec": timeout_sec,
                "started_at": started_at,
                "finished_at": finished_at,
                "exit_code": exit_code,
                "required": required,
                "status": status,
                "duration_ms": duration_ms,
                "stdout_path": stdout_path.as_posix(),
                "stderr_path": stderr_path.as_posix(),
            }
        )

    return records, required_failed
