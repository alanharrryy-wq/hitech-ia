from __future__ import annotations

def infer_dependency_hints(scan_report: dict) -> list[dict]:
    hints: list[dict] = []
    inventory = scan_report.get("inventory", [])
    rels = {str(item.get("relative_path", "")).lower() for item in inventory}
    languages = scan_report.get("signals", {}).get("language_counts", {})

    if "python" in languages:
        hints.append({
            "kind": "runtime",
            "name": "python_dependencies" if {"requirements.txt", "pyproject.toml"} & rels else "python_runtime",
            "confidence": "high" if {"requirements.txt", "pyproject.toml"} & rels else "medium",
        })
    if "javascript" in languages or "typescript" in languages:
        hints.append({
            "kind": "runtime",
            "name": "node_package_manager" if "package.json" in rels else "node_runtime",
            "confidence": "high" if "package.json" in rels else "medium",
        })
    if "go" in languages and "go.mod" in rels:
        hints.append({"kind": "runtime", "name": "go_modules", "confidence": "high"})
    if "rust" in languages and "cargo.toml" in rels:
        hints.append({"kind": "runtime", "name": "cargo", "confidence": "high"})

    hints.sort(key=lambda item: (item["kind"], item["name"]))
    return hints
