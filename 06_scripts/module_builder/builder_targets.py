from __future__ import annotations

from pathlib import Path

RUNTIME_LOCATIONS = {
    "scanner": "06_scripts/module_scanner/scan_module.py",
    "inference": "06_scripts/module_inference/infer_structure.py",
    "manifest": "06_scripts/module_manifest/build_manifest.py",
    "packaging": "06_scripts/module_packaging/package_module.py",
}

def runtime_paths(repo_root: Path) -> dict[str, Path]:
    return {name: (repo_root / rel).resolve() for name, rel in RUNTIME_LOCATIONS.items()}

def validate_runtime_paths(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for name, path in runtime_paths(repo_root).items():
        if not path.exists():
            errors.append(f"Missing runtime dependency for builder: {name} -> {path}")
    return errors
