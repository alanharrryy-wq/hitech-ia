from __future__ import annotations

from pathlib import Path

def generate_readme(spec: dict) -> str:
    lines = [
        f"# {spec['module_name']}",
        "",
        spec["summary"],
        "",
        "## Features",
        "",
    ]
    for feature in (spec.get("features") or ["Base module scaffold"]):
        lines.append(f"- {feature}")
    lines.extend(["", "## Exports", ""])
    for item in (spec.get("exports") or ["module info entrypoint"]):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)

def write_docs(spec: dict, workspace_root: Path) -> list[str]:
    created: list[str] = []
    readme_path = workspace_root / "docs" / "README.md"
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(generate_readme(spec), encoding="utf-8")
    created.append("docs/README.md")

    for idx, note in enumerate(spec.get("docs", []), start=1):
        doc_path = workspace_root / "docs" / f"note_{idx:02d}.md"
        doc_path.write_text(f"# Note {idx}\n\n{note}\n", encoding="utf-8")
        created.append(f"docs/note_{idx:02d}.md")
    return created
