from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from archive_quarantine import move_processed_zip, move_quarantine_zip
from build_registry import generate_registry_payload
from common import (
    ArchiveError,
    ExtractionSafetyError,
    RunContext,
    ValidationError,
    WiringError,
    collect_active_zip_artifacts,
    format_utc,
    repo_root_from_arg,
    reports_root_from_repo,
    resolve_inbox_root,
    run_id_for_project,
    runs_root_from_repo,
    utc_datetime_now,
    write_json,
)
from lock_manager import InstallLock
from make_install_plan import build_plan_payload
from manifest_validator import load_manifest_from_extracted, validate_and_normalize_manifest
from report_writer import build_report, write_report_files
from safe_extractor import extract_zip_safely
from test_executor import run_manifest_tests
from validate_inbox import build_validation_report
from wiring_engine import apply_operations, build_operations, rollback_package_changes

EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILURE = 1
EXIT_APPLY_FAILURE = 2
EXIT_TEST_FAILURE = 3
EXIT_LOCK_FAILURE = 4
EXIT_FINALIZATION_FAILURE = 5


def _create_run_context(repo_root: Path, project_slug: str, run_id: str | None = None) -> tuple[RunContext, dt.datetime]:
    started_dt = utc_datetime_now()
    resolved_run_id = run_id or run_id_for_project(project_slug, started_dt)

    runs_dir = runs_root_from_repo(repo_root) / resolved_run_id
    staging_dir = runs_dir / "staging"
    logs_dir = runs_dir / "logs"
    backups_dir = runs_dir / "backups"
    report_dir = reports_root_from_repo(repo_root) / project_slug / resolved_run_id

    for path in (runs_dir, staging_dir, logs_dir, backups_dir, report_dir):
        path.mkdir(parents=True, exist_ok=True)

    context = RunContext(
        repo_root=repo_root,
        project_slug=project_slug,
        run_id=resolved_run_id,
        started_at=format_utc(started_dt),
        runs_dir=runs_dir,
        staging_dir=staging_dir,
        logs_dir=logs_dir,
        backups_dir=backups_dir,
        report_dir=report_dir,
    )
    return context, started_dt


def _operation_record(
    *,
    package_slug: str,
    source: str,
    destination: str,
    action: str,
    result: str,
    duration_ms: int = 0,
    checksum_before: str | None = None,
    checksum_after: str | None = None,
    bytes_written: int = 0,
) -> dict:
    return {
        "package_slug": package_slug,
        "source": source,
        "destination": destination,
        "action": action,
        "result": result,
        "duration_ms": duration_ms,
        "bytes_written": bytes_written,
        "checksum_before": checksum_before,
        "checksum_after": checksum_after,
    }


def _status_from_outcome(applied_packages: list[str], failed_packages: list[str], quarantined_packages: list[str]) -> str:
    if not failed_packages and not quarantined_packages:
        return "success"
    if applied_packages:
        return "partial_failure"
    return "failure"


def run_pipeline(
    *,
    repo_root: Path,
    inbox_root: Path,
    project_slug: str,
    run_id: str | None,
    mode: str,
) -> tuple[dict, int]:
    context, started_dt = _create_run_context(repo_root, project_slug, run_id)

    validation_path = context.runs_dir / "01_validation_report.json"
    registry_before_path = context.runs_dir / "02_registry_before.json"
    install_plan_path = context.runs_dir / "03_install_plan.json"
    registry_after_path = context.runs_dir / "04_registry_after.json"

    operations: list[dict] = []
    test_records: list[dict] = []
    validated_sequences: list[int] = []
    applied_packages: list[str] = []
    failed_packages: list[str] = []
    quarantined_packages: list[str] = []
    exit_code = EXIT_SUCCESS

    lock = InstallLock(repo_root, context.run_id, project_slug)
    try:
        lock.acquire()
    except Exception as exc:  # noqa: BLE001
        report = build_report(
            run_id=context.run_id,
            project_slug=project_slug,
            started_at=context.started_at,
            finished_at=format_utc(utc_datetime_now()),
            status="failure",
            validated_sequences=[],
            applied_packages=[],
            quarantined_packages=[],
            failed_packages=[project_slug],
            tests=[],
            operations=[
                _operation_record(
                    package_slug=project_slug,
                    source=".install.lock",
                    destination=".install.lock",
                    action="acquire_lock",
                    result=f"failed: {exc}",
                )
            ],
        )
        write_report_files(report_dir=context.report_dir, report=report, logs_dir=context.logs_dir, backups_dir=context.backups_dir)
        return report, EXIT_LOCK_FAILURE

    try:
        validation_report = build_validation_report(inbox_root, project_slug)
        write_json(validation_path, validation_report)

        project_report = validation_report.get("projects", [{}])[0] if validation_report.get("projects") else {}
        invalid_paths = project_report.get("invalid_zip_paths", [])

        # Quarantine invalid ZIP artifacts discovered during validation.
        for rel_path in invalid_paths:
            source_zip = inbox_root / rel_path
            if not source_zip.exists():
                continue
            try:
                metadata = move_quarantine_zip(
                    repo_root=repo_root,
                    project_slug=project_slug,
                    source_zip=source_zip,
                    run_id=context.run_id,
                    reason="invalid_zip_contract",
                    when=started_dt,
                )
                operations.append(
                    _operation_record(
                        package_slug=source_zip.stem,
                        source=metadata["original_path"],
                        destination=metadata["final_path"],
                        action="quarantine",
                        result=metadata["result"],
                    )
                )
                quarantined_packages.append(source_zip.stem)
            except ArchiveError as exc:
                operations.append(
                    _operation_record(
                        package_slug=source_zip.stem,
                        source=source_zip.as_posix(),
                        destination="02_modules/_zip_quarantine",
                        action="quarantine",
                        result=f"failed: {exc}",
                    )
                )
                failed_packages.append(source_zip.stem)
                exit_code = EXIT_FINALIZATION_FAILURE

        registry_before = generate_registry_payload(
            repo_root=repo_root,
            inbox_root=inbox_root,
            project_slug=project_slug,
            validation_report=validation_report,
        )
        write_json(registry_before_path, registry_before)

        plan_payload, plan_code = build_plan_payload(
            registry_before,
            run_id=context.run_id,
            project_slug=project_slug,
        )
        write_json(install_plan_path, plan_payload)

        if exit_code == EXIT_SUCCESS and (not validation_report.get("valid", False) or plan_code != 0):
            exit_code = EXIT_VALIDATION_FAILURE

        if exit_code == EXIT_SUCCESS and mode == "apply":
            project_dir = inbox_root / project_slug
            artifacts = collect_active_zip_artifacts(project_dir, inbox_root)
            global_destinations: set[str] = set()

            for artifact in artifacts:
                validated_sequences.append(artifact.sequence)
                package_stage = context.staging_dir / f"{artifact.sequence:03d}_{artifact.package_slug}"
                package_log_dir = context.logs_dir / artifact.package_slug
                package_backup_dir = context.backups_dir / artifact.package_slug

                backup_entries: list[dict] = []
                created_files: list[Path] = []

                try:
                    extract_zip_safely(artifact.path, package_stage)
                    manifest_raw, manifest_path = load_manifest_from_extracted(package_stage)
                    manifest = validate_and_normalize_manifest(
                        manifest_raw,
                        artifact=artifact,
                        extracted_root=package_stage,
                        repo_root=repo_root,
                    )

                    operations_list = build_operations(
                        manifest,
                        extracted_root=package_stage,
                        repo_root=repo_root,
                        global_destinations=global_destinations,
                    )
                    operation_records, backup_entries, created_files = apply_operations(
                        operations_list,
                        repo_root=repo_root,
                        backup_root=package_backup_dir,
                    )
                    operations.extend(operation_records)
                    global_destinations.update(op["destination_rel"] for op in operations_list)

                    tests, required_failed = run_manifest_tests(
                        manifest.get("tests", []),
                        repo_root=repo_root,
                        logs_dir=package_log_dir,
                        package_slug=artifact.package_slug,
                    )
                    test_records.extend(tests)

                    if required_failed:
                        rollback_messages = rollback_package_changes(backups=backup_entries, created_files=created_files)
                        for message in rollback_messages:
                            operations.append(
                                _operation_record(
                                    package_slug=artifact.package_slug,
                                    source=artifact.filename,
                                    destination="rollback",
                                    action="rollback",
                                    result=message,
                                )
                            )

                        quarantine_meta = move_quarantine_zip(
                            repo_root=repo_root,
                            project_slug=project_slug,
                            source_zip=artifact.path,
                            run_id=context.run_id,
                            reason="required_test_failed",
                            when=started_dt,
                        )
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=quarantine_meta["original_path"],
                                destination=quarantine_meta["final_path"],
                                action="quarantine",
                                result=quarantine_meta["result"],
                            )
                        )
                        failed_packages.append(artifact.package_slug)
                        quarantined_packages.append(artifact.package_slug)
                        exit_code = EXIT_TEST_FAILURE
                        break

                    archive_meta = move_processed_zip(
                        repo_root=repo_root,
                        project_slug=project_slug,
                        source_zip=artifact.path,
                        run_id=context.run_id,
                        when=started_dt,
                    )
                    operations.append(
                        _operation_record(
                            package_slug=artifact.package_slug,
                            source=archive_meta["original_path"],
                            destination=archive_meta["final_path"],
                            action="archive",
                            result=archive_meta["result"],
                        )
                    )
                    applied_packages.append(artifact.package_slug)

                except (ExtractionSafetyError, ValidationError) as exc:
                    try:
                        quarantine_meta = move_quarantine_zip(
                            repo_root=repo_root,
                            project_slug=project_slug,
                            source_zip=artifact.path,
                            run_id=context.run_id,
                            reason=str(exc),
                            when=started_dt,
                        )
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=quarantine_meta["original_path"],
                                destination=quarantine_meta["final_path"],
                                action="quarantine",
                                result=quarantine_meta["result"],
                            )
                        )
                    except ArchiveError as archive_exc:
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=artifact.path.as_posix(),
                                destination="02_modules/_zip_quarantine",
                                action="quarantine",
                                result=f"failed: {archive_exc}",
                            )
                        )
                        exit_code = EXIT_FINALIZATION_FAILURE

                    failed_packages.append(artifact.package_slug)
                    quarantined_packages.append(artifact.package_slug)
                    if exit_code == EXIT_SUCCESS:
                        exit_code = EXIT_APPLY_FAILURE
                    break

                except WiringError as exc:
                    partial_records = getattr(exc, "operation_records", [])
                    backup_entries = getattr(exc, "backup_entries", backup_entries)
                    created_files = getattr(exc, "created_files", created_files)
                    operations.extend(partial_records)

                    rollback_messages = rollback_package_changes(backups=backup_entries, created_files=created_files)
                    for message in rollback_messages:
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=artifact.filename,
                                destination="rollback",
                                action="rollback",
                                result=message,
                            )
                        )

                    try:
                        quarantine_meta = move_quarantine_zip(
                            repo_root=repo_root,
                            project_slug=project_slug,
                            source_zip=artifact.path,
                            run_id=context.run_id,
                            reason=str(exc),
                            when=started_dt,
                        )
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=quarantine_meta["original_path"],
                                destination=quarantine_meta["final_path"],
                                action="quarantine",
                                result=quarantine_meta["result"],
                            )
                        )
                    except ArchiveError as archive_exc:
                        operations.append(
                            _operation_record(
                                package_slug=artifact.package_slug,
                                source=artifact.path.as_posix(),
                                destination="02_modules/_zip_quarantine",
                                action="quarantine",
                                result=f"failed: {archive_exc}",
                            )
                        )
                        exit_code = EXIT_FINALIZATION_FAILURE

                    failed_packages.append(artifact.package_slug)
                    quarantined_packages.append(artifact.package_slug)
                    if exit_code == EXIT_SUCCESS:
                        exit_code = EXIT_APPLY_FAILURE
                    break

                except ArchiveError as exc:
                    failed_packages.append(artifact.package_slug)
                    operations.append(
                        _operation_record(
                            package_slug=artifact.package_slug,
                            source=artifact.path.as_posix(),
                            destination="archive/quarantine",
                            action="finalize",
                            result=f"failed: {exc}",
                        )
                    )
                    exit_code = EXIT_FINALIZATION_FAILURE
                    break

                except Exception as exc:  # noqa: BLE001
                    failed_packages.append(artifact.package_slug)
                    operations.append(
                        _operation_record(
                            package_slug=artifact.package_slug,
                            source=artifact.path.as_posix(),
                            destination="pipeline",
                            action="apply",
                            result=f"failed: {exc}",
                        )
                    )
                    if exit_code == EXIT_SUCCESS:
                        exit_code = EXIT_APPLY_FAILURE
                    break

        registry_after = generate_registry_payload(
            repo_root=repo_root,
            inbox_root=inbox_root,
            project_slug=project_slug,
        )
        write_json(registry_after_path, registry_after)

    finally:
        try:
            lock.release()
        except Exception:  # noqa: BLE001
            if exit_code == EXIT_SUCCESS:
                exit_code = EXIT_LOCK_FAILURE

    finished_at = format_utc(utc_datetime_now())
    status = _status_from_outcome(applied_packages, failed_packages, quarantined_packages)
    if exit_code == EXIT_SUCCESS and mode == "dry_run":
        status = "success"

    report = build_report(
        run_id=context.run_id,
        project_slug=project_slug,
        started_at=context.started_at,
        finished_at=finished_at,
        status=status,
        validated_sequences=validated_sequences,
        applied_packages=applied_packages,
        quarantined_packages=quarantined_packages,
        failed_packages=failed_packages,
        tests=test_records,
        operations=operations,
    )
    write_report_files(report_dir=context.report_dir, report=report, logs_dir=context.logs_dir, backups_dir=context.backups_dir)

    return report, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full ZIP inbox lifecycle")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--inbox-root", help="Optional inbox root override")
    parser.add_argument("--run-id", help="Optional deterministic run id")
    parser.add_argument("--mode", choices=["apply", "dry_run"], default="apply")
    args = parser.parse_args()

    repo_root = repo_root_from_arg(args.repo_root)
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    report, code = run_pipeline(
        repo_root=repo_root,
        inbox_root=inbox_root,
        project_slug=args.project,
        run_id=args.run_id,
        mode=args.mode,
    )

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"run_id: {report['run_id']}")
    print(f"project: {report['project_slug']}")
    print(f"report_status: {report['status']}")
    print(f"report_path: {(reports_root_from_repo(repo_root) / args.project / report['run_id'] / 'report.json').as_posix()}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
