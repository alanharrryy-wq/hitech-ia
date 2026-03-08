from __future__ import annotations

from pathlib import PurePosixPath

CONFIG_NAMES = {
    "package.json", "pnpm-lock.yaml", "package-lock.json", "requirements.txt",
    "pyproject.toml", "poetry.lock", "go.mod", "cargo.toml", ".env.example",
}

def suggest_destination(relative_path: str) -> str:
    pure = PurePosixPath(relative_path)
    rel_lower = relative_path.lower()
    parts_lower = [part.lower() for part in pure.parts]

    if "src" in parts_lower:
        idx = parts_lower.index("src")
        suffix = PurePosixPath(*pure.parts[idx + 1 :]).as_posix()
        return f"src/{suffix}" if suffix else "src"
    if "tests" in parts_lower:
        idx = parts_lower.index("tests")
        suffix = PurePosixPath(*pure.parts[idx + 1 :]).as_posix()
        return f"tests/{suffix}" if suffix else "tests"
    if "test" in parts_lower:
        idx = parts_lower.index("test")
        suffix = PurePosixPath(*pure.parts[idx + 1 :]).as_posix()
        return f"tests/{suffix}" if suffix else "tests"
    if "docs" in parts_lower or rel_lower.endswith(".md") or rel_lower.endswith(".rst"):
        if "docs" in parts_lower:
            suffix = PurePosixPath(*pure.parts[parts_lower.index("docs") + 1 :]).as_posix()
            return f"docs/{suffix}" if suffix else "docs"
        return f"docs/{pure.name}"
    if pure.name.lower() in CONFIG_NAMES or pure.suffix.lower() in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return f"config/{pure.name}"
    return f"assets/{relative_path}"

def infer_target_suggestions(scan_report: dict) -> list[dict]:
    suggestions: list[dict] = []
    for item in scan_report.get("inventory", []):
        if item.get("is_noise") or item.get("is_suspicious"):
            continue
        if not item.get("is_textish"):
            continue
        rel = str(item.get("relative_path", ""))
        suggestions.append({
            "source": rel,
            "destination": suggest_destination(rel),
            "required": True,
            "reason": "deterministic_path_mapping",
        })
    suggestions.sort(key=lambda x: (x["destination"].lower(), x["source"].lower()))
    return suggestions
