from __future__ import annotations

def build_ingest_report(
    *,
    built_at: str,
    repo_root: str,
    mode: str,
    watch: bool,
    interval_sec: int,
    iterations: int,
    queue_snapshots: list[list[dict]],
    runs: list[dict],
    warnings: list[str],
    errors: list[str],
) -> dict:
    return {
        "schema_version": "1.0",
        "built_at": built_at,
        "repo_root": repo_root,
        "mode": mode,
        "watch": watch,
        "interval_sec": interval_sec,
        "iterations": iterations,
        "queue_snapshots": queue_snapshots,
        "runs": runs,
        "warnings": warnings,
        "errors": errors,
        "is_valid": len(errors) == 0,
    }
