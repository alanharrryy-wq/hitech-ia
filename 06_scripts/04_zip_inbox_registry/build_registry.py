from __future__ import annotations

from pathlib import Path

from common import (
    ZipInfo,
    collect_active_zip_infos,
    collect_archived_zip_infos,
    default_arg_parser,
    read_json,
    resolve_inbox_root,
    sequence_status_from_infos,
    utc_now,
    write_json,
)
from validate_inbox import build_validation_report

ARCHIVE_STATE_ORDER = {
    "inbox": 0,
    "processed": 1,
    "failed": 2,
    "quarantined": 3,
}


def _entry_from_info(
    info: ZipInfo,
    *,
    status: str,
    validation_status: str,
    install_plan_eligible: bool,
    archive_state: str,
    archive_path: str | None,
    findings: list[str] | None = None,
) -> dict:
    return {
        "sequence": info.sequence,
        "project_slug": info.project_slug,
        "package_slug": info.package_slug,
        "filename": info.filename,
        "source_zip_file": info.filename,
        "relative_path": info.relative_path,
        "sha256": info.sha256,
        "status": status,
        "validation_status": validation_status,
        "install_plan_eligible": install_plan_eligible,
        "archive_state": archive_state,
        "archive_path": archive_path,
        "size_bytes": info.size_bytes,
        "findings": findings or [],
        "last_seen_utc": info.modified_at_utc,
    }


def _registry_for_project(project: dict, inbox_root: Path) -> dict:
    slug = project["project_slug"]
    project_dir = inbox_root / slug

    active_infos = collect_active_zip_infos(project_dir, inbox_root)
    archived_processed = collect_archived_zip_infos(project_dir, inbox_root, "_processed")
    archived_failed = collect_archived_zip_infos(project_dir, inbox_root, "_failed")
    archived_quarantine = collect_archived_zip_infos(project_dir, inbox_root, "_quarantine")

    seq_status = project["sequence_status"]
    project_validation_status = "pass" if project["valid"] else "fail"
    install_plan_eligible = project["valid"] and project["zip_count"] > 0 and bool(seq_status["is_contiguous"])

    active_status = "validated" if install_plan_eligible else "pending"
    active_entries = [
        _entry_from_info(
            info,
            status=active_status,
            validation_status=project_validation_status,
            install_plan_eligible=install_plan_eligible,
            archive_state="inbox",
            archive_path=None,
            findings=project["errors"],
        )
        for info in active_infos
    ]

    processed_entries = [
        _entry_from_info(
            info,
            status="processed",
            validation_status="pass",
            install_plan_eligible=False,
            archive_state="processed",
            archive_path=info.relative_path,
        )
        for info in archived_processed
    ]
    failed_entries = [
        _entry_from_info(
            info,
            status="failed",
            validation_status="fail",
            install_plan_eligible=False,
            archive_state="failed",
            archive_path=info.relative_path,
        )
        for info in archived_failed
    ]
    quarantined_entries = [
        _entry_from_info(
            info,
            status="quarantined",
            validation_status="fail",
            install_plan_eligible=False,
            archive_state="quarantined",
            archive_path=info.relative_path,
        )
        for info in archived_quarantine
    ]

    packages = active_entries + processed_entries + failed_entries + quarantined_entries
    packages.sort(
        key=lambda entry: (
            ARCHIVE_STATE_ORDER.get(str(entry["archive_state"]), 99),
            int(entry["sequence"]),
            str(entry["filename"]).lower(),
        )
    )

    if active_entries:
        project_state = "ready" if install_plan_eligible else "blocked"
    elif packages:
        project_state = "processed"
    else:
        project_state = "idle"

    counts = {
        "inbox": len(active_entries),
        "processed": len(processed_entries),
        "failed": len(failed_entries),
        "quarantined": len(quarantined_entries),
    }

    return {
        "project_slug": slug,
        "project_state": project_state,
        "validation_status": project_validation_status,
        "install_plan_eligible": install_plan_eligible,
        "sequence_status": seq_status,
        "findings": project["errors"],
        "package_counts": counts,
        "packages": packages,
    }


def generate_registry_payload(
    inbox_root: Path,
    validation_report: dict | None = None,
) -> dict:
    validation = validation_report or build_validation_report(inbox_root)
    projects = sorted(validation.get("projects", []), key=lambda project: project["project_slug"])

    registry_projects = [_registry_for_project(project, inbox_root) for project in projects]

    return {
        "registry_schema_version": "1.1.0",
        "generated_at_utc": utc_now(),
        "inbox_root": str(inbox_root),
        "projects": registry_projects,
        "invalid_zip_files": validation.get("invalid_zip_files", []),
        "validation_summary": validation.get("summary", {}),
        "validation_passed": bool(validation.get("valid")),
    }


def main() -> int:
    parser = default_arg_parser("Build ZIP inbox internal registry")
    parser.add_argument("--validation-report", help="Optional pre-generated validation report")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)
    validation_report = read_json(Path(args.validation_report)) if args.validation_report else None

    payload = generate_registry_payload(inbox_root, validation_report)
    write_json(Path(args.output), payload)

    print("STATUS: PASS")
    print(f"projects: {len(payload['projects'])}")
    print(f"validation_passed: {payload['validation_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
