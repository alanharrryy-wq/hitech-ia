from __future__ import annotations

import zipfile
from pathlib import Path, PurePosixPath

from language_fingerprints import guess_language

NOISE_PATH_PARTS = {
    "__pycache__", ".pytest_cache", "node_modules", "dist", "build",
    ".next", ".turbo", ".cache", ".mypy_cache",
}
NOISE_FILENAMES = {".ds_store", "thumbs.db", ".coverage"}
SUSPICIOUS_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".bin", ".msi", ".pkg", ".deb", ".rpm", ".pem", ".key", ".p12", ".jks"}
NESTED_ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"}
TEXT_EXTENSIONS = {
    ".py", ".pyi", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".jsonc",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".rst", ".txt", ".html", ".css",
    ".scss", ".sass", ".less", ".sh", ".ps1", ".psm1", ".bat", ".cmd", ".go", ".rs",
    ".java", ".kt", ".swift", ".php", ".rb", ".cs", ".cpp", ".cc", ".cxx", ".c", ".h",
    ".hpp", ".sql", ".xml", ".svg",
}

def _normalize_rel(path_value: str) -> str:
    return str(PurePosixPath(path_value.replace("\\", "/")))

def _top_level_dir(path_value: str) -> str | None:
    pure = PurePosixPath(path_value)
    parts = [part for part in pure.parts if part not in {"", "."}]
    if len(parts) <= 1:
        return None
    return parts[0]

def is_noise_path(path_value: str) -> bool:
    pure = PurePosixPath(path_value.lower())
    if pure.name in NOISE_FILENAMES:
        return True
    return any(part in NOISE_PATH_PARTS for part in pure.parts)

def suspicious_reason(path_value: str) -> str | None:
    pure = PurePosixPath(path_value)
    name_lower = pure.name.lower()
    suffix_lower = pure.suffix.lower()
    if any(part == ".." for part in pure.parts):
        return "path_traversal"
    if suffix_lower in SUSPICIOUS_EXTENSIONS:
        return f"suspicious_extension:{suffix_lower}"
    if suffix_lower in NESTED_ARCHIVE_EXTENSIONS:
        return f"nested_archive:{suffix_lower}"
    if "id_rsa" in name_lower or name_lower.endswith(".pem") or name_lower.endswith(".key"):
        return "secret_material"
    return None

def classify_textish(path_value: str) -> bool:
    pure = PurePosixPath(path_value)
    suffix_lower = pure.suffix.lower()
    if not suffix_lower:
        return pure.name.lower() in {"dockerfile", "makefile", "readme", "license"}
    return suffix_lower in TEXT_EXTENSIONS

def inventory_from_zip(zip_path: Path) -> tuple[list[dict], list[str]]:
    inventory: list[dict] = []
    warnings: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        infos = sorted(archive.infolist(), key=lambda item: item.filename.lower())
        for info in infos:
            member = info.filename.replace("\\", "/")
            if not member or member.endswith("/"):
                continue
            rel = _normalize_rel(member)
            reason = suspicious_reason(rel)
            if reason == "path_traversal":
                warnings.append(f"Unsafe ZIP member detected: {rel}")
            inventory.append({
                "relative_path": rel,
                "extension": PurePosixPath(rel).suffix.lower(),
                "size_bytes": int(info.file_size),
                "kind": "archive_member",
                "top_level_dir": _top_level_dir(rel),
                "language_guess": guess_language(rel),
                "is_noise": is_noise_path(rel),
                "is_suspicious": reason is not None,
                "suspicious_reason": reason,
                "is_textish": classify_textish(rel),
            })
    return inventory, warnings

def inventory_from_directory(root: Path) -> tuple[list[dict], list[str]]:
    inventory: list[dict] = []
    warnings: list[str] = []
    files = [path for path in root.rglob("*") if path.is_file()]
    files.sort(key=lambda path: path.as_posix().lower())
    for file_path in files:
        rel = _normalize_rel(file_path.relative_to(root).as_posix())
        size_bytes = int(file_path.stat().st_size)
        reason = suspicious_reason(rel)
        inventory.append({
            "relative_path": rel,
            "extension": file_path.suffix.lower(),
            "size_bytes": size_bytes,
            "kind": "file",
            "top_level_dir": _top_level_dir(rel),
            "language_guess": guess_language(rel),
            "is_noise": is_noise_path(rel),
            "is_suspicious": reason is not None,
            "suspicious_reason": reason,
            "is_textish": classify_textish(rel),
        })
        if size_bytes > 5 * 1024 * 1024:
            warnings.append(f"Oversized file detected: {rel} ({size_bytes} bytes)")
    return inventory, warnings

def inventory_from_input(input_path: Path) -> tuple[str, list[dict], list[str]]:
    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        inventory, warnings = inventory_from_zip(input_path)
        return "zip", inventory, warnings
    if input_path.is_dir():
        inventory, warnings = inventory_from_directory(input_path)
        return "directory", inventory, warnings
    raise ValueError(f"Unsupported input path for scanner: {input_path}")
