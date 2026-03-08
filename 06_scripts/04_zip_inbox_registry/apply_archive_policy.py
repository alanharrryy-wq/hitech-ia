from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    archive_zip,
    collect_active_zip_infos,
    parse_sequences,
    resolve_inbox_root,
    utc_now,
    write_json,
)

TARGET_MAP = {
    "failed": "_failed",
    "quarantine": "_quarantine",
}


def apply_archive_policy(
    inbox_root: Path,
    project_slug: str,
    *,
    target: str,
    run_id: str,
    sequences: list[int] | None = None,
    filenames: list[str] | None = None,
) -> tuple[dict, int]:
    slug = project_slug.lower()
    project_dir = inbox_root / slug
    requested_sequences = sorted(set(sequences or []))
    requested_filenames = sorted(set(filenames or []), key=str.lower)

    moved: list[dict] = []
    skipped: list[str] = []

    if not project_dir.exists():
        payload = {
            "archive_manifest_version": "1.1.0",
            "generated_at_utc": utc_now(),
            "project_slug": slug,
            "archive_state": target,
            "archive_folder": None,
            "requested_sequences": requested_sequences,
            "requested_filenames": requested_filenames,
            "moved": [],
            "skipped": [f"Project folder does not exist: {project_dir}"],
        }
        return payload, 1

    candidates = collect_active_zip_infos(project_dir, inbox_root)
    if requested_sequences:
        candidates = [item for item in candidates if item.sequence in requested_sequences]
    if requested_filenames:
        wanted = {name.lower() for name in requested_filenames}
        candidates = [item for item in candidates if item.filename.lower() in wanted]

    archive_folder = project_dir / TARGET_MAP[target] / run_id
    for item in candidates:
        source = project_dir / item.filename
        destination = archive_folder / item.filename
        archive_zip(source, destination)
        moved.append(
            {
                "sequence": item.sequence,
                "filename": item.filename,
                "from": str(source),
                "to": str(destination),
            }
        )

    if requested_sequences and not moved:
        skipped.append("No ZIP matched requested sequence filters")
    if requested_filenames and not moved:
        skipped.append("No ZIP matched requested filename filters")

    payload = {
        "archive_manifest_version": "1.1.0",
        "generated_at_utc": utc_now(),
        "project_slug": slug,
        "archive_state": target,
        "archive_folder": str(archive_folder),
        "requested_sequences": requested_sequences,
        "requested_filenames": requested_filenames,
        "moved": moved,
        "skipped": skipped,
    }
    exit_code = 0 if moved or (not requested_sequences and not requested_filenames) else 1
    return payload, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Move pending ZIP packages to failed or quarantine archive")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--inbox-root", help="Optional inbox override path")
    parser.add_argument("--target", choices=sorted(TARGET_MAP), default="failed")
    parser.add_argument("--run-id", help="Archive run id folder (default UTC timestamp)")
    parser.add_argument("--sequences", help="Comma-separated sequence filter")
    parser.add_argument("--filenames", nargs="*", help="Explicit filename filter")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)
    run_id = args.run_id or utc_now().replace(":", "").replace("-", "")

    payload, code = apply_archive_policy(
        inbox_root,
        args.project_slug,
        target=args.target,
        run_id=run_id,
        sequences=parse_sequences(args.sequences),
        filenames=args.filenames,
    )
    write_json(Path(args.output), payload)

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"archived: {len(payload['moved'])}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
