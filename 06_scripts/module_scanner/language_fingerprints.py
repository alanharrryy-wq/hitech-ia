from __future__ import annotations

from pathlib import PurePosixPath

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".json": "json", ".jsonc": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".ini": "ini", ".cfg": "ini",
    ".md": "markdown", ".rst": "markdown", ".txt": "text",
    ".html": "html", ".css": "css", ".scss": "css", ".sass": "css", ".less": "css",
    ".sh": "shell", ".ps1": "powershell", ".psm1": "powershell", ".bat": "batch", ".cmd": "batch",
    ".go": "go", ".rs": "rust", ".java": "java", ".kt": "kotlin", ".swift": "swift",
    ".php": "php", ".rb": "ruby", ".cs": "csharp",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp",
    ".sql": "sql", ".xml": "xml", ".svg": "svg",
}

SPECIAL_FILENAMES: dict[str, str] = {
    "dockerfile": "docker",
    "makefile": "make",
    "readme": "markdown",
    "license": "text",
    "requirements.txt": "python",
    "package.json": "javascript",
    "pnpm-lock.yaml": "javascript",
    "package-lock.json": "javascript",
    "cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
}

def guess_language(path_value: str) -> str | None:
    pure = PurePosixPath(path_value)
    name_lower = pure.name.lower()
    stem_lower = pure.stem.lower()
    suffix_lower = pure.suffix.lower()
    if name_lower in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[name_lower]
    if stem_lower in SPECIAL_FILENAMES and not suffix_lower:
        return SPECIAL_FILENAMES[stem_lower]
    if suffix_lower in EXTENSION_LANGUAGE_MAP:
        return EXTENSION_LANGUAGE_MAP[suffix_lower]
    return None

def probable_primary_language(language_counts: dict[str, int]) -> str | None:
    if not language_counts:
        return None
    ranked = sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[0][0]
