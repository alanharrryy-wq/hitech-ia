from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from autofix_manifest import autofix_manifest
from manifest_diff import build_manifest_diff
from manifest_report import build_manifest_report
from validate_manifest_contract import validate_manifest_contract

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def load_json_if_exists(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def build_manifest(*, inference_report_path: Path, output_manifest_path: Path, output_report_path: Path, existing_manifest_path: Path | None = None) -> dict:
    inference_report = json.loads(inference_report_path.read_text(encoding="utf-8"))
    existing_manifest = load_json_if_exists(existing_manifest_path)

    manifest, metadata, warnings = autofix_manifest(existing_manifest, inference_report)
    validation_errors = validate_manifest_contract(manifest)
    diff_text = build_manifest_diff(existing_manifest, manifest)

    write_json(output_manifest_path, manifest)
    report = build_manifest_report(
        manifest_path=output_manifest_path.resolve().as_posix(),
        source_inference_report=inference_report_path.resolve().as_posix(),
        manifest=manifest,
        metadata=metadata,
        warnings=warnings,
        validation_errors=validation_errors,
        diff_text=diff_text,
        built_at=utc_now(),
    )
    write_json(output_report_path, report)
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description="Build or autofix manifest from inference report")
    parser.add_argument("--inference-report", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--existing-manifest")
    args = parser.parse_args()

    report = build_manifest(
        inference_report_path=Path(args.inference_report),
        output_manifest_path=Path(args.output_manifest),
        output_report_path=Path(args.output_report),
        existing_manifest_path=Path(args.existing_manifest) if args.existing_manifest else None,
    )

    print("STATUS:", "PASS" if report["is_valid"] else "FAIL")
    print(f"manifest_path: {report['manifest_path']}")
    print(f"warning_count: {len(report['warnings'])}")
    print(f"validation_error_count: {len(report['validation_errors'])}")
    return 0 if report["is_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
