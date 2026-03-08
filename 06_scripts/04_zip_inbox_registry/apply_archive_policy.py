from __future__ import annotations

import argparse
from pathlib import Path

from archive_quarantine import move_quarantine_zip
from common import (
    collect_active_zip_artifacts,
    inbox_root_from_repo,
    parse_sequences,
    repo_root_from_arg,
    utc_datetime_now,
    utc_now,
    write_json,
)


def apply_archive_policy(
    *,
    repo_root: Path,
    project_slug: str,
    run_id: str,
    reason: str,
    sequences: list[int] | None = None,
    zip_names: list[str] | None = None,
) -> tuple[dict, int]:
    inbox_root = inbox_root_from_repo(repo_root)
    project_dir = inbox_root / project_slug
    when = utc_datetime_now()

    requested_sequences = sorted(set(sequences or []))
    requested_names = sorted(set(zip_names or []), key=str.lower)

    moved: list[dict] = []
    skipped: list[str] = []

    if not project_dir.exists():
        skipped.append(f"Project inbox folder not found: {project_dir}")
    else:
        artifacts = collect_active_zip_artifacts(project_dir, inbox_root)
        if requested_sequences:
            artifacts = [item for item in artifacts if item.sequence in requested_sequences]
        if requested_names:
            wanted = {value.lower() for value in requested_names}
            artifacts = [item for item in artifacts if item.filename.lower() in wanted]

        for artifact in artifacts:
            moved.append(
                move_quarantine_zip(
                    repo_root=repo_root,
                    project_slug=project_slug,
                    source_zip=artifact.path,
                    run_id=run_id,
                    reason=reason,
                    when=when,
                )
            )

        if not artifacts:
            skipped.append("No ZIP artifacts matched filters")

    payload = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "run_id": run_id,
        "project_slug": project_slug,
        "state": "quarantined",
        "reason": reason,
        "requested_sequences": requested_sequences,
        "requested_zip_names": requested_names,
        "moved": moved,
        "skipped": skipped,
    }
    code = 0 if moved else 1
    return payload, code


def main() -> int:
    parser = argparse.ArgumentParser(description="Move ZIP artifacts to canonical quarantine root")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--project", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reason", default="policy_quarantine")
    parser.add_argument("--sequences", help="Comma-separated sequence filter")
    parser.add_argument("--zip-names", nargs="*", help="Specific ZIP filename filter")
    args = parser.parse_args()

    repo_root = repo_root_from_arg(args.repo_root)

    payload, code = apply_archive_policy(
        repo_root=repo_root,
        project_slug=args.project,
        run_id=args.run_id,
        reason=args.reason,
        sequences=parse_sequences(args.sequences),
        zip_names=args.zip_names,
    )
    write_json(Path(args.output), payload)

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"quarantined: {len(payload['moved'])}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
