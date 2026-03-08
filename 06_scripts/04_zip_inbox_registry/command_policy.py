from __future__ import annotations

import shlex
from pathlib import Path

from common import ValidationError, resolve_safe_relative_path


DEFAULT_TEST_TIMEOUT_SEC = 300
MIN_TEST_TIMEOUT_SEC = 1
MAX_TEST_TIMEOUT_SEC = 3600


def _as_non_empty_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} must be a non-empty string")
    return cleaned


def normalize_command_spec(test: dict, *, index: int) -> tuple[list[str], str]:
    has_args = "args" in test and test.get("args") is not None
    has_command = "command" in test and str(test.get("command", "")).strip()

    if has_args:
        args_payload = test.get("args")
        if not isinstance(args_payload, list) or not args_payload:
            raise ValidationError(f"tests[{index}] args must be a non-empty array of strings")
        args: list[str] = []
        for arg_index, entry in enumerate(args_payload):
            if not isinstance(entry, str) or not entry.strip():
                raise ValidationError(f"tests[{index}] args[{arg_index}] must be a non-empty string")
            args.append(entry)
        display_command = " ".join(shlex.quote(arg) for arg in args)
        return args, display_command

    if has_command:
        command = _as_non_empty_string(test.get("command"), field_name=f"tests[{index}] command")
        try:
            # Use POSIX tokenization consistently so quoted legacy commands
            # (e.g. python -c "import sys; sys.exit(1)") are parsed into args
            # without keeping wrapper quotes on Windows.
            parsed = shlex.split(command, posix=True)
        except ValueError as exc:
            raise ValidationError(f"tests[{index}] command could not be parsed: {exc}") from exc
        if not parsed:
            raise ValidationError(f"tests[{index}] command resolved to zero arguments")
        return parsed, command

    raise ValidationError(f"tests[{index}] requires either command or args")


def normalize_test_cwd(value: object, *, index: int) -> str:
    if value is None:
        return "."
    cwd = _as_non_empty_string(value, field_name=f"tests[{index}] cwd")
    return resolve_safe_relative_path(cwd)


def normalize_test_timeout(value: object, *, index: int) -> int:
    if value is None:
        return DEFAULT_TEST_TIMEOUT_SEC
    try:
        timeout_sec = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"tests[{index}] timeout_sec must be an integer") from exc
    if timeout_sec < MIN_TEST_TIMEOUT_SEC or timeout_sec > MAX_TEST_TIMEOUT_SEC:
        raise ValidationError(
            f"tests[{index}] timeout_sec must be between {MIN_TEST_TIMEOUT_SEC} and {MAX_TEST_TIMEOUT_SEC}"
        )
    return timeout_sec


def normalize_test_env(value: object, *, index: int) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"tests[{index}] env must be an object")
    normalized: dict[str, str] = {}
    for key, env_value in sorted(value.items(), key=lambda item: str(item[0]).lower()):
        if not isinstance(key, str) or not key.strip():
            raise ValidationError(f"tests[{index}] env keys must be non-empty strings")
        if not isinstance(env_value, str):
            raise ValidationError(f"tests[{index}] env[{key}] must be a string")
        normalized[key] = env_value
    return normalized


def resolve_test_cwd(repo_root: Path, cwd_rel: str) -> Path:
    resolved = (repo_root / cwd_rel).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ValidationError(f"Test cwd escapes repo root: {cwd_rel}") from exc
    return resolved
