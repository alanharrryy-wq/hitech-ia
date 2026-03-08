#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ZIP_RE = re.compile(r"^zip(?P<seq>\d+)_(?P<project>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$")

def validate_project(project_dir: Path) -> dict:
    findings = []
    packages = []
    seen_sequences = {}
    for item in sorted(project_dir.iterdir(), key=lambda p: p.name.lower()):
        if item.name.startswith("_"):
            continue
        if item.is_dir():
            findings.append(f"Unexpected directory in project folder: {item.name}")
            continue
        if item.suffix.lower() != ".zip":
            if item.name != "project.manifest.json":
                findings.append(f"Unexpected non-ZIP file: {item.name}")
            continue
        m = ZIP_RE.match(item.name)
        if not m:
            findings.append(f"Invalid ZIP filename: {item.name}")
            continue
        seq = int(m.group("seq"))
        project = m.group("project")
        package = m.group("package")
        if project != project_dir.name:
            findings.append(f"Foreign project slug in filename: {item.name}")
        if seq in seen_sequences:
            findings.append(f"Duplicate sequence {seq}: {item.name} and {seen_sequences[seq]}")
        else:
            seen_sequences[seq] = item.name
        packages.append({"sequence": seq, "project_slug": project, "package_slug": package, "filename": item.name})
    sequences = sorted(pkg["sequence"] for pkg in packages)
    if sequences:
        missing = [n for n in range(min(sequences), max(sequences)+1) if n not in sequences]
        if missing:
            findings.append(f"Sequence gaps detected: {missing}")
    return {"project_slug": project_dir.name, "package_count": len(packages), "packages": sorted(packages, key=lambda x: x["sequence"]), "findings": findings, "valid": len(findings) == 0}

def main():
    parser = argparse.ArgumentParser(description="Validate ZIP inbox structure.")
    parser.add_argument("inbox_root", help="Path to _zip_inbox root")
    args = parser.parse_args()
    inbox_root = Path(args.inbox_root).resolve()
    if not inbox_root.exists():
        raise SystemExit(f"Inbox root does not exist: {inbox_root}")
    results = []
    for child in sorted(inbox_root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and not child.name.startswith("_"):
            results.append(validate_project(child))
    output = {"inbox_root": str(inbox_root), "project_count": len(results), "results": results, "all_valid": all(r["valid"] for r in results)}
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
