from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from common import utc_now, write_json

PAIRS = [
    ("01_project_manifest.schema.json", "01_project_manifest.example.json"),
    ("03_registry.schema.json", "02_registry.example.json"),
    ("04_install_request.schema.json", "03_install_request.example.json"),
    ("05_install_plan.schema.json", "04_install_plan.example.json"),
    ("06_install_report.schema.json", "05_install_report.example.json"),
    ("07_target_map.schema.json", "06_target_map.example.json"),
    ("08_inbox_index.schema.json", "07_inbox_index.example.json"),
    ("09_validation_report.schema.json", "09_validation_report.example.json"),
    ("10_archive_manifest.schema.json", "10_archive_manifest.example.json"),
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate zip-inbox JSON examples against schemas")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    schema_root = repo_root / "08_schemas" / "06_zip_inbox_registry"
    example_root = repo_root / "09_examples" / "06_zip_inbox_registry"

    results: list[dict] = []
    failures: list[str] = []

    for schema_name, example_name in PAIRS:
        schema_path = schema_root / schema_name
        example_path = example_root / example_name

        if not schema_path.exists():
            message = f"Missing schema: {schema_path}"
            failures.append(message)
            results.append({"schema": schema_name, "example": example_name, "valid": False, "errors": [message]})
            continue
        if not example_path.exists():
            message = f"Missing example: {example_path}"
            failures.append(message)
            results.append({"schema": schema_name, "example": example_name, "valid": False, "errors": [message]})
            continue

        schema = _load_json(schema_path)
        example = _load_json(example_path)

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(example), key=lambda err: list(err.path))
        error_messages = [error.message for error in errors]

        valid = len(error_messages) == 0
        if not valid:
            failures.extend([f"{example_name}: {message}" for message in error_messages])

        results.append(
            {
                "schema": schema_name,
                "example": example_name,
                "valid": valid,
                "errors": error_messages,
            }
        )

    payload = {
        "report_version": "1.0.0",
        "generated_at_utc": utc_now(),
        "schema_root": str(schema_root),
        "example_root": str(example_root),
        "all_valid": len(failures) == 0,
        "results": results,
    }

    write_json(Path(args.output), payload)
    print("STATUS:", "PASS" if payload["all_valid"] else "FAIL")
    print(f"pairs_validated: {len(results)}")
    return 0 if payload["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
