#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Move ZIPs into _failed or quarantine.")
    parser.add_argument("project_folder")
    parser.add_argument("--target", choices=["_failed", "_quarantine"], default="_failed")
    parser.add_argument("zip_filenames", nargs="+")
    args = parser.parse_args()
    project_folder = Path(args.project_folder).resolve()
    target_dir = project_folder / args.target
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in args.zip_filenames:
        source = project_folder / filename
        target = target_dir / filename
        if not source.exists():
            raise SystemExit(f"ZIP not found: {source}")
        shutil.move(str(source), str(target))
        print(target)

if __name__ == "__main__":
    main()
