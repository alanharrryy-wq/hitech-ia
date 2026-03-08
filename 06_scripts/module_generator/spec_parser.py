from __future__ import annotations

import json
import re
from pathlib import Path

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}

def slugify(value: str) -> str:
    value = value.strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value

def normalize_module_spec(spec: dict) -> tuple[dict, list[str]]:
    if not isinstance(spec, dict):
        raise ValueError("module spec must be an object")

    required = ["project_slug", "package_slug", "module_name", "language", "summary"]
    missing = [field for field in required if not spec.get(field)]
    if missing:
        raise ValueError("Missing required spec fields: " + ", ".join(missing))

    language = str(spec["language"]).strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    warnings: list[str] = []
    project_hint = spec.get("project_hint")
    if project_hint:
        project_hint = slugify(str(project_hint))
        warnings.append("project_hint_supplied")

    normalized = {
        "project_slug": slugify(str(spec["project_slug"])),
        "package_slug": slugify(str(spec["package_slug"])),
        "module_name": str(spec["module_name"]).strip(),
        "language": language,
        "summary": str(spec["summary"]).strip(),
        "features": [str(item).strip() for item in spec.get("features", []) if str(item).strip()],
        "exports": [str(item).strip() for item in spec.get("exports", []) if str(item).strip()],
        "tests": [str(item).strip() for item in spec.get("tests", []) if str(item).strip()],
        "docs": [str(item).strip() for item in spec.get("docs", []) if str(item).strip()],
        "project_hint": project_hint,
        "entrypoint_name": slugify(str(spec.get("entrypoint_name") or spec["package_slug"])),
    }
    return normalized, warnings

def load_and_normalize_spec(path: Path) -> tuple[dict, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return normalize_module_spec(payload)
