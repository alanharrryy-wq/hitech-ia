from __future__ import annotations

from pathlib import Path

from common import write_json


def build_report(
    *,
    run_id: str,
    project_slug: str,
    started_at: str,
    finished_at: str,
    status: str,
    validated_sequences: list[int],
    applied_packages: list[str],
    quarantined_packages: list[str],
    failed_packages: list[str],
    tests: list[dict],
    operations: list[dict],
) -> dict:
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "project_slug": project_slug,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "validated_sequences": sorted(validated_sequences),
        "applied_packages": applied_packages,
        "quarantined_packages": quarantined_packages,
        "failed_packages": failed_packages,
        "tests": tests,
        "operations": operations,
        "summary": {
            "zip_count": len(validated_sequences),
            "applied_count": len(applied_packages),
            "failed_count": len(failed_packages),
            "quarantined_count": len(quarantined_packages),
        },
    }


def write_report_files(
    *,
    report_dir: Path,
    report: dict,
    logs_dir: Path,
    backups_dir: Path,
) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.json"
    summary_path = report_dir / "summary.md"

    write_json(report_path, report)

    lines = [
        "# ZIP Inbox Run Summary",
        "",
        f"- run_id: `{report['run_id']}`",
        f"- project_slug: `{report['project_slug']}`",
        f"- status: `{report['status']}`",
        f"- validated_sequences: `{report['validated_sequences']}`",
        f"- applied_packages: `{report['applied_packages']}`",
        f"- failed_packages: `{report['failed_packages']}`",
        f"- quarantined_packages: `{report['quarantined_packages']}`",
        "",
        "## Paths",
        "",
        f"- report_json: `{report_path.as_posix()}`",
        f"- logs_dir: `{logs_dir.as_posix()}`",
        f"- backups_dir: `{backups_dir.as_posix()}`",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path, summary_path
