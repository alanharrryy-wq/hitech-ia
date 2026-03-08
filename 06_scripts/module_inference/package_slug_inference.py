from __future__ import annotations

import re
from collections import Counter
from pathlib import PurePosixPath

GENERIC_NAMES = {
    "src", "source", "app", "apps", "lib", "libs", "code", "module",
    "tests", "test", "docs", "doc", "assets", "config", "configs",
}

def slugify(value: str) -> str:
    value = value.strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "module_core"

def infer_package_slug(scan_report: dict) -> tuple[str, list[str]]:
    warnings: list[str] = []
    inventory = list(scan_report.get("inventory", []))
    top_dirs = Counter()
    file_stems = Counter()

    for item in inventory:
        if item.get("is_noise"):
            continue
        rel = str(item.get("relative_path", ""))
        pure = PurePosixPath(rel)
        parts = [part for part in pure.parts if part not in {"", "."}]
        if parts:
            first = slugify(parts[0])
            if first and first not in GENERIC_NAMES:
                top_dirs[first] += 1
        stem = slugify(pure.stem)
        if stem and stem not in GENERIC_NAMES:
            file_stems[stem] += 1

    ranked = sorted(top_dirs.items(), key=lambda item: (-item[1], item[0]))
    if ranked:
        return ranked[0][0], warnings

    fallback_stems = sorted(file_stems.items(), key=lambda item: (-item[1], item[0]))
    if fallback_stems:
        warnings.append("Package slug inferred from filename fallback")
        return fallback_stems[0][0], warnings

    primary = scan_report.get("signals", {}).get("probable_primary_language")
    if primary:
        warnings.append("Package slug inferred from primary language fallback")
        return slugify(f"{primary}_core"), warnings

    warnings.append("Package slug fell back to module_core")
    return "module_core", warnings
