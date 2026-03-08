from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from apply_runner import run_project_pipeline
from inbox_watcher import watch_project_queue
from ingest_report import build_ingest_report


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def auto_ingest(
    *,
    repo_root: Path,
    output_report: Path,
    project_filter: str | None = None,
    mode: str = "dry_run",
    watch: bool = False,
    interval_sec: int = 15,
    max_loops: int = 1,
) -> dict:
    warnings: list[str] = []
    errors: list[str] = []
    queue_snapshots: list[list[dict]] = []
    runs: list[dict] = []

    loops = max_loops if watch else 1
    for queue in watch_project_queue(
        repo_root=repo_root,
        project_filter=project_filter,
        interval_sec=interval_sec,
        max_loops=loops,
    ):
        queue_snapshots.append(queue)
        for item in queue:
            run_id = f"auto_ingest_{item['project_slug']}"
            result = run_project_pipeline(
                repo_root=repo_root,
                project_slug=item["project_slug"],
                mode=mode,
                run_id=run_id,
            )
            runs.append(result)
            if result["status"] != "success":
                errors.append(f"project_failed:{item['project_slug']}")

    if not queue_snapshots or all(len(snapshot) == 0 for snapshot in queue_snapshots):
        warnings.append("No eligible projects found in inbox")

    report = build_ingest_report(
        built_at=utc_now(),
        repo_root=repo_root.resolve().as_posix(),
        mode=mode,
        watch=watch,
        interval_sec=interval_sec,
        iterations=len(queue_snapshots),
        queue_snapshots=queue_snapshots,
        runs=runs,
        warnings=warnings,
        errors=errors,
    )
    write_json(output_report, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto ingest pending module ZIPs from _zip_inbox")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--project")
    parser.add_argument("--mode", default="dry_run", choices=["dry_run", "apply"])
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-sec", type=int, default=15)
    parser.add_argument("--max-loops", type=int, default=1)
    args = parser.parse_args()

    report = auto_ingest(
        repo_root=Path(args.repo_root).resolve(),
        output_report=Path(args.output_report).resolve(),
        project_filter=args.project,
        mode=args.mode,
        watch=args.watch,
        interval_sec=args.interval_sec,
        max_loops=args.max_loops,
    )
    print("STATUS:", "PASS" if report["is_valid"] else "FAIL")
    print(f"iterations: {report['iterations']}")
    print(f"projects_run: {len(report['runs'])}")
    print(f"report_path: {Path(args.output_report).resolve().as_posix()}")
    return 0 if report["is_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
