#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    parser = argparse.ArgumentParser(description="Generate deterministic install plan from registry.")
    parser.add_argument("registry_json")
    parser.add_argument("project_slug")
    parser.add_argument("--mode", choices=["dry_run", "apply"], default="dry_run")
    parser.add_argument("--output", default="install_plan.generated.json")
    args = parser.parse_args()
    registry = load_json(Path(args.registry_json).resolve())
    project = next((entry for entry in registry.get("projects", []) if entry.get("project_slug") == args.project_slug), None)
    if not project:
        raise SystemExit(f"Project not found in registry: {args.project_slug}")
    packages = sorted(project.get("packages", []), key=lambda x: x["sequence"])
    actions = [
        {"step": 1, "action": "validate_inbox"},
        {"step": 2, "action": "read_project_manifest"},
        {"step": 3, "action": "acquire_lock"},
        {"step": 4, "action": "extract_to_staging"},
        {"step": 5, "action": "validate_staged_content"},
        {"step": 6, "action": "route_contract_assets"},
        {"step": 7, "action": "route_runtime_assets"},
        {"step": 8, "action": "apply_wiring"},
        {"step": 9, "action": "run_quality_gates"},
        {"step": 10, "action": "write_report_and_ledger"},
        {"step": 11, "action": "archive_or_quarantine"},
        {"step": 12, "action": "release_lock"}
    ]
    plan = {
        "plan_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_slug": args.project_slug,
        "mode": args.mode,
        "packages": packages,
        "actions": actions,
        "quality_gates": [
            "filename_valid",
            "no_duplicate_sequences",
            "manifest_present_or_defaults_approved",
            "route_destinations_allowed",
            "tests_passed",
            "report_written"
        ]
    }
    output_path = Path(args.output).resolve()
    output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(output_path)

if __name__ == "__main__":
    main()
