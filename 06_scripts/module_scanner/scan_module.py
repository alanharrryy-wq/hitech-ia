from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from archive_inventory import inventory_from_input
from scan_report import build_scan_report

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def scan_input(input_path: Path) -> dict:
    resolved = input_path.resolve()
    input_type, inventory, warnings = inventory_from_input(resolved)
    return build_scan_report(
        input_path=resolved.as_posix(),
        input_type=input_type,
        inventory=inventory,
        warnings=warnings,
        scanned_at=utc_now(),
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Scan raw ZIP or source folder into deterministic scan report")
    parser.add_argument("--input", required=True, help="Path to ZIP or directory")
    parser.add_argument("--output", required=True, help="Path to output report JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"Input path does not exist: {input_path}")

    report = scan_input(input_path)
    write_json(output_path, report)

    print("STATUS: PASS")
    print(f"input_type: {report['input_type']}")
    print(f"file_count: {report['summary']['file_count']}")
    print(f"noise_count: {report['summary']['noise_count']}")
    print(f"suspicious_count: {report['summary']['suspicious_count']}")
    print(f"primary_language: {report['signals']['probable_primary_language']}")
    print(f"report_path: {output_path.resolve().as_posix()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
