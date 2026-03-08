from __future__ import annotations

import argparse
from pathlib import Path

from build_registry import generate_registry_payload
from common import read_json, resolve_inbox_root, utc_now, write_json


def _build_actions(mode: str) -> list[dict]:
    actions = [
        {"step": 1, "action": "discover_inbox"},
        {"step": 2, "action": "validate_naming_order_and_isolation"},
        {"step": 3, "action": "refresh_internal_registry"},
        {"step": 4, "action": "load_project_manifest_or_defaults"},
        {"step": 5, "action": "extract_zip_to_staging"},
        {"step": 6, "action": "route_contract_reference_assets"},
        {"step": 7, "action": "route_runtime_executable_assets"},
        {"step": 8, "action": "apply_wiring"},
        {"step": 9, "action": "run_quality_gates"},
        {"step": 10, "action": "write_install_report_and_ledger"},
        {"step": 11, "action": "archive_processed_or_failed_packages"},
    ]
    if mode == "apply":
        actions.append({"step": 12, "action": "finalize_apply_cycle"})
    return actions


def build_plan_payload(registry: dict, project_slug: str, mode: str) -> tuple[dict, int]:
    slug = project_slug.lower()
    project = next((item for item in registry.get("projects", []) if item.get("project_slug") == slug), None)

    if not project:
        payload = {
            "plan_version": "1.1.0",
            "generated_at_utc": utc_now(),
            "project_slug": slug,
            "mode": mode,
            "plan_status": "blocked",
            "install_plan_eligible": False,
            "blocked_reasons": [f"Project slug not found in registry: {slug}"],
            "sequence_status": {
                "is_contiguous": False,
                "present_sequences": [],
                "missing_sequences": [],
                "duplicate_sequences": [],
            },
            "packages": [],
            "actions": _build_actions(mode),
            "quality_gates": [],
            "routing_model": {
                "destination_classes": [
                    "contract_reference",
                    "runtime_executable",
                ]
            },
        }
        return payload, 1

    candidate_packages = [
        package for package in project.get("packages", []) if package.get("archive_state") == "inbox"
    ]
    candidate_packages.sort(key=lambda package: (int(package["sequence"]), str(package["filename"]).lower()))

    blocked_reasons: list[str] = []
    if not project.get("install_plan_eligible"):
        blocked_reasons.append("Project is not install-plan eligible according to registry validation state")
    if not candidate_packages:
        blocked_reasons.append("No pending ZIP packages found in inbox for this project")

    sequence_status = project.get("sequence_status", {})
    if not sequence_status.get("is_contiguous", False):
        blocked_reasons.append("Sequence is not contiguous")

    plan_status = "ready" if len(blocked_reasons) == 0 else "blocked"
    package_status = "planned" if plan_status == "ready" else "pending"

    packages = []
    for package in candidate_packages:
        record = dict(package)
        record["status"] = package_status
        record["install_plan_eligible"] = plan_status == "ready"
        packages.append(record)

    payload = {
        "plan_version": "1.1.0",
        "generated_at_utc": utc_now(),
        "project_slug": slug,
        "mode": mode,
        "plan_status": plan_status,
        "install_plan_eligible": plan_status == "ready",
        "blocked_reasons": blocked_reasons,
        "sequence_status": sequence_status,
        "packages": packages,
        "actions": _build_actions(mode),
        "quality_gates": [
            "filename_valid",
            "project_folder_isolation_valid",
            "sequence_contiguous",
            "no_duplicate_sequences",
            "routing_destinations_allowed",
            "report_written",
        ],
        "routing_model": {
            "destination_classes": [
                "contract_reference",
                "runtime_executable",
            ]
        },
    }
    return payload, 0 if plan_status == "ready" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic install plan for one project slug")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--inbox-root", help="Optional inbox override path")
    parser.add_argument("--registry-input", help="Optional pre-generated registry JSON")
    parser.add_argument("--mode", choices=["dry_run", "apply"], default="dry_run")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    if args.registry_input:
        registry = read_json(Path(args.registry_input))
    else:
        registry = generate_registry_payload(inbox_root)

    payload, code = build_plan_payload(registry, args.project_slug, args.mode)
    write_json(Path(args.output), payload)

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"project_slug: {payload['project_slug']}")
    print(f"plan_status: {payload['plan_status']}")
    print(f"packages: {len(payload['packages'])}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
