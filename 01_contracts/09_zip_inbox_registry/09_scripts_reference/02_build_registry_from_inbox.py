#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ZIP_RE = re.compile(r"^zip(?P<seq>\d+)_(?P<project>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$")

def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def scan_project(project_dir: Path) -> dict:
    packages, findings, sequences = [], [], {}
    for item in sorted(project_dir.iterdir(), key=lambda p: p.name.lower()):
        if item.name.startswith("_") or item.is_dir() or item.suffix.lower() != ".zip":
            continue
        m = ZIP_RE.match(item.name)
        if not m:
            findings.append(f"Invalid ZIP filename: {item.name}")
            continue
        seq = int(m.group("seq")); project = m.group("project"); package = m.group("package")
        if project != project_dir.name:
            findings.append(f"Foreign project slug: {item.name}")
        if seq in sequences:
            findings.append(f"Duplicate sequence {seq}: {item.name} and {sequences[seq]}")
        sequences[seq] = item.name
        stat = item.stat()
        packages.append({
            "sequence": seq, "project_slug": project, "package_slug": package, "filename": item.name,
            "sha256": sha256_of_file(item), "size_bytes": stat.st_size, "status": "pending",
            "findings": [], "archive_path": None,
            "last_seen_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        })
    packages.sort(key=lambda x: x["sequence"])
    state = "ready" if packages and not findings else "blocked" if findings else "idle"
    return {"project_slug": project_dir.name, "project_state": state, "findings": findings, "packages": packages}

def main():
    parser = argparse.ArgumentParser(description="Build registry JSON from ZIP inbox.")
    parser.add_argument("inbox_root")
    parser.add_argument("--output", default="registry.generated.json")
    args = parser.parse_args()
    inbox_root = Path(args.inbox_root).resolve()
    projects = [scan_project(child) for child in sorted(inbox_root.iterdir(), key=lambda p: p.name.lower()) if child.is_dir() and not child.name.startswith("_")]
    registry = {"registry_schema_version": "1.0.0", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "projects": projects}
    output_path = Path(args.output).resolve()
    output_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(output_path)

if __name__ == "__main__":
    main()
