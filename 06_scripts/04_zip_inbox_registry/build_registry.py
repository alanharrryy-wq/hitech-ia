from __future__ import annotations

from pathlib import Path

from common import (
    archive_root_from_repo,
    default_arg_parser,
    parse_zip_name,
    quarantine_root_from_repo,
    repo_root_from_arg,
    resolve_inbox_root,
    sha256_file,
    utc_now,
    write_json,
)
from validate_inbox import build_validation_report


STATUS_ORDER = {
    "pending": 0,
    "validated": 1,
    "planned": 2,
    "applied": 3,
    "processed": 4,
    "failed": 5,
    "quarantined": 6,
}


def _item_key(item: dict) -> tuple[int, str, int]:
    return (int(item["sequence"]), str(item["zip_name"]).lower(), STATUS_ORDER.get(item["status"], 99))


def _archive_or_quarantine_items(repo_root: Path, project_slug: str, state: str) -> list[dict]:
    base_root = archive_root_from_repo(repo_root) if state == "processed" else quarantine_root_from_repo(repo_root)
    project_root = base_root / project_slug
    items: list[dict] = []
    if not project_root.exists():
        return items

    for zip_path in sorted(project_root.rglob("*.zip"), key=lambda path: path.as_posix().lower()):
        parsed = parse_zip_name(zip_path.name)
        if not parsed:
            continue
        items.append(
            {
                "sequence": parsed.sequence,
                "zip_name": zip_path.name,
                "package_slug": parsed.package_slug,
                "sha256": sha256_file(zip_path),
                "size_bytes": zip_path.stat().st_size,
                "status": state,
                "archive_path": zip_path.as_posix() if state == "processed" else None,
                "quarantine_path": zip_path.as_posix() if state == "quarantined" else None,
                "manifest_path": None,
                "errors": [],
                "warnings": [],
            }
        )

    return items


def _project_registry(validation_project: dict, repo_root: Path, inbox_root: Path) -> dict:
    slug = validation_project["project_slug"]
    project_dir = inbox_root / slug

    project_errors = list(validation_project.get("errors", []))
    project_warnings = list(validation_project.get("warnings", []))
    project_valid = bool(validation_project.get("valid"))

    items: list[dict] = []

    for zip_item in validation_project.get("valid_zips", []):
        zip_path = Path(zip_item["absolute_path"])
        status = "validated" if project_valid else "failed"
        item_errors = project_errors if not project_valid else []

        items.append(
            {
                "sequence": int(zip_item["sequence"]),
                "zip_name": zip_item["zip_name"],
                "package_slug": zip_item["package_slug"],
                "sha256": sha256_file(zip_path),
                "size_bytes": zip_path.stat().st_size,
                "status": status,
                "archive_path": None,
                "quarantine_path": None,
                "manifest_path": None,
                "errors": item_errors,
                "warnings": project_warnings,
            }
        )

    items.extend(_archive_or_quarantine_items(repo_root, slug, "processed"))
    items.extend(_archive_or_quarantine_items(repo_root, slug, "quarantined"))

    items.sort(key=_item_key)

    return {
        "schema_version": "1.0",
        "project_slug": slug,
        "generated_at": utc_now(),
        "items": items,
    }


def generate_registry_payload(
    *,
    repo_root: Path,
    inbox_root: Path,
    project_slug: str | None = None,
    validation_report: dict | None = None,
) -> dict:
    validation = validation_report or build_validation_report(inbox_root, project_slug)
    project_reports = validation.get("projects", [])

    if project_slug:
        if not project_reports:
            return {
                "schema_version": "1.0",
                "project_slug": project_slug,
                "generated_at": utc_now(),
                "items": [],
            }
        return _project_registry(project_reports[0], repo_root, inbox_root)

    registries = [_project_registry(project_report, repo_root, inbox_root) for project_report in project_reports]
    registries.sort(key=lambda item: item["project_slug"])
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "projects": registries,
    }


def main() -> int:
    parser = default_arg_parser("Build ZIP inbox registry snapshot")
    parser.add_argument("--project", help="Optional project slug filter")
    parser.add_argument("--validation-report", help="Optional pre-generated validation report path")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = repo_root_from_arg(args.repo_root)
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    validation_report = None
    if args.validation_report:
        import json

        validation_report = json.loads(Path(args.validation_report).read_text(encoding="utf-8"))

    payload = generate_registry_payload(
        repo_root=repo_root,
        inbox_root=inbox_root,
        project_slug=args.project,
        validation_report=validation_report,
    )
    write_json(Path(args.output), payload)

    print("STATUS: PASS")
    if args.project:
        print(f"items: {len(payload.get('items', []))}")
    else:
        print(f"projects: {len(payload.get('projects', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
