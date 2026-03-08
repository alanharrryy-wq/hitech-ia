from __future__ import annotations

import argparse
from pathlib import Path

from apply_archive_policy import apply_archive_policy
from archive_processed import archive_processed
from build_registry import generate_registry_payload
from common import reports_root_from_repo, resolve_inbox_root, runs_root_from_repo, utc_now, write_json
from make_install_plan import build_plan_payload
from validate_inbox import build_validation_report


def _default_run_id() -> str:
    return utc_now().replace("-", "").replace(":", "")


def _write_summary(
    summary_path: Path,
    *,
    run_id: str,
    mode: str,
    project_slug: str,
    validation_report: dict,
    plan_payload: dict,
    archive_manifest: dict | None,
    outputs: dict[str, Path],
    on_failure: str,
) -> None:
    lines = [
        "# ZIP Inbox Full-Cycle Run Summary",
        "",
        f"- run_id: `{run_id}`",
        f"- mode: `{mode}`",
        f"- project_slug: `{project_slug}`",
        f"- validation_valid: `{validation_report.get('valid')}`",
        f"- plan_status: `{plan_payload.get('plan_status')}`",
        f"- install_plan_eligible: `{plan_payload.get('install_plan_eligible')}`",
        f"- on_failure_policy: `{on_failure}`",
        "",
        "## Counts",
        "",
        f"- projects_detected: `{validation_report.get('summary', {}).get('project_count', 0)}`",
        f"- zip_count: `{validation_report.get('summary', {}).get('zip_count', 0)}`",
        f"- errors: `{validation_report.get('summary', {}).get('error_count', 0)}`",
        f"- warnings: `{validation_report.get('summary', {}).get('warning_count', 0)}`",
        f"- plan_packages: `{len(plan_payload.get('packages', []))}`",
    ]

    if archive_manifest:
        lines.extend(
            [
                f"- archived_count: `{len(archive_manifest.get('moved', []))}`",
                f"- archive_state: `{archive_manifest.get('archive_state')}`",
            ]
        )

    lines.extend(["", "## Outputs", ""])
    for label, path in outputs.items():
        lines.append(f"- {label}: `{path}`")

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run validation, registry, install-plan generation, and optional archive handling"
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--mode", choices=["dry_run", "apply"], default="dry_run")
    parser.add_argument("--inbox-root", help="Optional inbox override path")
    parser.add_argument(
        "--on-failure",
        choices=["leave_pending", "move_to_failed", "move_to_quarantine"],
        default="leave_pending",
    )
    parser.add_argument("--run-id", help="Optional deterministic run id")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    slug = args.project_slug.lower()
    run_id = args.run_id or _default_run_id()
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    run_dir = runs_root_from_repo(repo_root) / slug / run_id
    report_path = reports_root_from_repo(repo_root) / slug / f"{run_id}.md"
    run_dir.mkdir(parents=True, exist_ok=True)

    validation_path = run_dir / "01_validation_report.json"
    registry_before_path = run_dir / "02_registry_snapshot_before.json"
    plan_path = run_dir / "03_install_plan.json"
    archive_path = run_dir / "04_archive_manifest.json"
    validation_after_path = run_dir / "05_validation_report_after.json"
    registry_after_path = run_dir / "06_registry_snapshot_after.json"

    validation_report = build_validation_report(inbox_root)
    write_json(validation_path, validation_report)

    registry_before = generate_registry_payload(inbox_root, validation_report)
    write_json(registry_before_path, registry_before)

    plan_payload, plan_code = build_plan_payload(registry_before, slug, args.mode)
    write_json(plan_path, plan_payload)

    archive_manifest: dict | None = None
    outputs: dict[str, Path] = {
        "validation_report": validation_path,
        "registry_before": registry_before_path,
        "install_plan": plan_path,
    }

    if args.mode == "apply" and plan_payload.get("plan_status") == "ready":
        sequences = [int(package["sequence"]) for package in plan_payload.get("packages", [])]
        archive_manifest, archive_code = archive_processed(
            inbox_root,
            slug,
            run_id=run_id,
            sequences=sequences,
        )
        write_json(archive_path, archive_manifest)
        outputs["archive_manifest"] = archive_path

        validation_after = build_validation_report(inbox_root)
        write_json(validation_after_path, validation_after)
        outputs["validation_after"] = validation_after_path

        registry_after = generate_registry_payload(inbox_root, validation_after)
        write_json(registry_after_path, registry_after)
        outputs["registry_after"] = registry_after_path

        success = validation_report.get("valid", False) and plan_code == 0 and archive_code == 0
    elif args.mode == "apply" and plan_payload.get("plan_status") != "ready":
        archive_code = 0
        if args.on_failure != "leave_pending":
            target = "failed" if args.on_failure == "move_to_failed" else "quarantine"
            sequences = [int(package["sequence"]) for package in plan_payload.get("packages", [])]
            archive_manifest, archive_code = apply_archive_policy(
                inbox_root,
                slug,
                target=target,
                run_id=run_id,
                sequences=sequences,
            )
            write_json(archive_path, archive_manifest)
            outputs["archive_manifest"] = archive_path

            validation_after = build_validation_report(inbox_root)
            write_json(validation_after_path, validation_after)
            outputs["validation_after"] = validation_after_path

            registry_after = generate_registry_payload(inbox_root, validation_after)
            write_json(registry_after_path, registry_after)
            outputs["registry_after"] = registry_after_path

        success = False
    else:
        success = validation_report.get("valid", False) and plan_code == 0

    _write_summary(
        report_path,
        run_id=run_id,
        mode=args.mode,
        project_slug=slug,
        validation_report=validation_report,
        plan_payload=plan_payload,
        archive_manifest=archive_manifest,
        outputs=outputs,
        on_failure=args.on_failure,
    )

    print("STATUS:", "PASS" if success else "FAIL")
    print(f"run_id: {run_id}")
    print(f"summary: {report_path}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
