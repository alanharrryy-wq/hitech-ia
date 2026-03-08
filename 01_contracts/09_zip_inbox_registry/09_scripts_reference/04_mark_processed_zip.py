#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Move ZIPs into _processed after successful apply.")
    parser.add_argument("project_folder")
    parser.add_argument("zip_filenames", nargs="+")
    args = parser.parse_args()
    project_folder = Path(args.project_folder).resolve()
    processed_dir = project_folder / "_processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    for filename in args.zip_filenames:
        source = project_folder / filename
        target = processed_dir / filename
        if not source.exists():
            raise SystemExit(f"ZIP not found: {source}")
        shutil.move(str(source), str(target))
        print(target)

if __name__ == "__main__":
    main()
