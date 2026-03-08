from __future__ import annotations

import re
import shlex
from pathlib import PurePosixPath

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

def slugify(value: str) -> str:
    value = value.strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value

def normalize_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Path must be a non-empty string")
    candidate = value.replace("\\", "/").strip()
    if candidate.startswith("/") or re.match(r"^[a-zA-Z]:", candidate):
        raise ValueError(f"Absolute path is not allowed: {value}")
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"Path traversal is not allowed: {value}")
    return pure.as_posix()

def normalize_env(value: dict | None) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("env must be an object")
    normalized = {}
    for key in sorted(value):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("env keys must be non-empty strings")
        normalized[str(key)] = str(value[key])
    return normalized

def normalize_test_entry(test: dict, index: int = 0) -> tuple[dict, list[str]]:
    if not isinstance(test, dict):
        raise ValueError(f"tests[{index}] must be an object")

    warnings: list[str] = []
    name = str(test.get("name") or f"test_{index + 1}").strip()
    test_type = str(test.get("type") or "command").strip().lower()
    if test_type != "command":
        raise ValueError(f"tests[{index}] unsupported type: {test_type}")

    args = test.get("args")
    command = test.get("command")
    if args is None:
        if command:
            parsed = shlex.split(str(command), posix=False)
            if not parsed:
                raise ValueError(f"tests[{index}] command cannot be empty")
            args = parsed
            warnings.append("legacy_command_string_normalized")
        else:
            raise ValueError(f"tests[{index}] requires args or command")
    if not isinstance(args, list) or not args:
        raise ValueError(f"tests[{index}] args must be a non-empty array")

    normalized_args = [str(item) for item in args if str(item).strip()]
    if not normalized_args:
        raise ValueError(f"tests[{index}] args cannot be empty")

    cwd = test.get("cwd")
    normalized_cwd = normalize_relative_path(str(cwd)) if cwd else None

    timeout_sec = int(test.get("timeout_sec", 120))
    if timeout_sec < 1 or timeout_sec > 3600:
        raise ValueError(f"tests[{index}] timeout_sec out of allowed range")

    normalized = {
        "name": name,
        "type": test_type,
        "args": normalized_args,
        "required": bool(test.get("required", True)),
        "timeout_sec": timeout_sec,
        "env": normalize_env(test.get("env")),
    }
    if normalized_cwd:
        normalized["cwd"] = normalized_cwd

    return normalized, warnings

def normalize_tests(payload: list) -> tuple[list[dict], list[str]]:
    if payload is None:
        return [], []
    if not isinstance(payload, list):
        raise ValueError("tests must be an array")
    warnings: list[str] = []
    normalized = []
    for index, test in enumerate(payload):
        entry, entry_warnings = normalize_test_entry(test, index=index)
        normalized.append(entry)
        warnings.extend(entry_warnings)
    normalized.sort(key=lambda item: (item["name"].lower(), item["type"]))
    return normalized, warnings

def validate_slug(name: str, field_name: str) -> str:
    candidate = slugify(name)
    if not candidate or not SLUG_PATTERN.fullmatch(candidate):
        raise ValueError(f"{field_name} must be lowercase underscore slug")
    return candidate
