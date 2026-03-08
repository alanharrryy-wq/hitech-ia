from __future__ import annotations

from collections import Counter
from pathlib import PurePosixPath

from language_fingerprints import probable_primary_language

def build_scan_report(*, input_path: str, input_type: str, inventory: list[dict], warnings: list[str], scanned_at: str) -> dict:
    language_counts: Counter[str] = Counter()
    top_level_dirs: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    has_tests = False
    has_docs = False
    has_src = False
    has_manifest_candidate = False
    noise_count = 0
    suspicious_count = 0
    textish_count = 0

    for item in inventory:
        language = item.get("language_guess")
        if language:
            language_counts[language] += 1
        extension = str(item.get("extension") or "")
        if extension:
            extension_counts[extension] += 1
        top_dir = item.get("top_level_dir")
        if top_dir:
            top_level_dirs[str(top_dir)] += 1
        rel = str(item["relative_path"]).lower()
        parts = PurePosixPath(rel).parts
        if "tests" in parts or "test" in parts:
            has_tests = True
        if "docs" in parts or rel.endswith(".md") or rel.endswith(".rst"):
            has_docs = True
        if "src" in parts:
            has_src = True
        if rel.endswith("manifest.json") or rel.endswith(".hitech/manifest.json"):
            has_manifest_candidate = True
        if item.get("is_noise"):
            noise_count += 1
        if item.get("is_suspicious"):
            suspicious_count += 1
        if item.get("is_textish"):
            textish_count += 1

    return {
        "schema_version": "1.0",
        "scanned_at": scanned_at,
        "input_path": input_path,
        "input_type": input_type,
        "inventory": inventory,
        "summary": {
            "file_count": len(inventory),
            "noise_count": noise_count,
            "suspicious_count": suspicious_count,
            "textish_count": textish_count,
            "binaryish_count": max(len(inventory) - textish_count, 0),
        },
        "signals": {
            "language_counts": dict(sorted(language_counts.items())),
            "extension_counts": dict(sorted(extension_counts.items())),
            "top_level_dirs": dict(sorted(top_level_dirs.items())),
            "probable_primary_language": probable_primary_language(dict(language_counts)),
            "has_tests": has_tests,
            "has_docs": has_docs,
            "has_src": has_src,
            "has_manifest_candidate": has_manifest_candidate,
        },
        "warnings": sorted(set(warnings)),
    }
