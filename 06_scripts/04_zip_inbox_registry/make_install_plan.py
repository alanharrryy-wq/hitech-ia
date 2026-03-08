from __future__ import annotations

import argparse
from pathlib import Path

from build_registry import generate_registry_payload
from common import repo_root_from_arg, resolve_inbox_root, run_id_for_project, sequence_status_from_values, utc_datetime_now, write_json


def build_plan_payload(registry: dict, *, run_id: str, project_slug: str) -> tuple[dict, int]:
    items = list(registry.get("items", []))
    active_items = [item for item in items if item.get("status") in {"validated", "pending", "failed"} and not item.get("archive_path") and not item.get("quarantine_path")]
    active_items.sort(key=lambda item: (int(item["sequence"]), str(item["zip_name"]).lower()))

    errors: list[str] = []
    if not active_items:
        errors.append("No installable ZIP artifacts available for project")

    invalid_states = [item for item in active_items if item.get("status") != "validated"]
    if invalid_states:
        errors.append("Registry has non-validated pending items")

    seq_status = sequence_status_from_values([int(item["sequence"]) for item in active_items])
    if seq_status["duplicate_sequences"]:
        errors.append("Duplicate sequence numbers detected")
    if seq_status["missing_sequences"]:
        errors.append("Sequence gaps detected")

    steps: list[dict] = [
        {"type": "validate_inbox", "status": "pending"},
        {"type": "build_registry", "status": "pending"},
    ]

    for item in active_items:
        steps.append(
            {
                "type": "extract_zip",
                "sequence": int(item["sequence"]),
                "package_slug": item["package_slug"],
                "zip_name": item["zip_name"],
                "status": "pending",
            }
        )
        steps.append(
            {
                "type": "apply_targets",
                "sequence": int(item["sequence"]),
                "package_slug": item["package_slug"],
                "zip_name": item["zip_name"],
                "status": "pending",
            }
        )
        steps.append(
            {
                "type": "run_tests",
                "sequence": int(item["sequence"]),
                "package_slug": item["package_slug"],
                "zip_name": item["zip_name"],
                "status": "pending",
            }
        )

    steps.append({"type": "archive_processed", "status": "pending"})

    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "project_slug": project_slug,
        "sequence_status": seq_status,
        "errors": errors,
        "steps": steps,
    }

    return payload, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Create deterministic install plan")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--inbox-root", help="Optional inbox override path")
    parser.add_argument("--registry-input", help="Optional registry JSON path")
    parser.add_argument("--run-id", help="Optional run id")
    args = parser.parse_args()

    repo_root = repo_root_from_arg(args.repo_root)
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)
    run_id = args.run_id or run_id_for_project(args.project, utc_datetime_now())

    if args.registry_input:
        import json

        registry = json.loads(Path(args.registry_input).read_text(encoding="utf-8"))
    else:
        registry = generate_registry_payload(
            repo_root=repo_root,
            inbox_root=inbox_root,
            project_slug=args.project,
        )

    payload, code = build_plan_payload(registry, run_id=run_id, project_slug=args.project)
    write_json(Path(args.output), payload)

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"steps: {len(payload['steps'])}")
    if payload["errors"]:
        print("errors:", "; ".join(payload["errors"]))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
