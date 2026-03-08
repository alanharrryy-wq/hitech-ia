from __future__ import annotations

from pathlib import Path

from common import (
    ALLOWED_PROJECT_INTERNAL_DIRS,
    ALLOWED_PROJECT_NON_ZIP_FILES,
    collect_project_dirs,
    default_arg_parser,
    normalize,
    parse_zip_name,
    repo_root_from_arg,
    resolve_inbox_root,
    sequence_status_from_values,
    utc_now,
    write_json,
)


def _project_validation(project_dir: Path, inbox_root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    valid_zips: list[dict] = []
    invalid_zip_paths: list[str] = []

    for entry in sorted(project_dir.iterdir(), key=lambda item: item.name.lower()):
        rel = normalize(entry.relative_to(inbox_root))

        if entry.is_dir():
            if entry.name in ALLOWED_PROJECT_INTERNAL_DIRS:
                continue
            if entry.name.startswith("_"):
                warnings.append(f"Unknown reserved directory: {rel}")
            else:
                warnings.append(f"Unexpected directory in project inbox: {rel}")
            continue

        if entry.name in ALLOWED_PROJECT_NON_ZIP_FILES or entry.name == "project.manifest.json":
            continue

        if entry.suffix.lower() != ".zip":
            warnings.append(f"Unexpected non-ZIP file in project inbox: {rel}")
            continue

        parsed = parse_zip_name(entry.name)
        if not parsed:
            errors.append(f"Invalid ZIP filename: {rel}")
            invalid_zip_paths.append(rel)
            continue

        if parsed.project_slug != project_dir.name:
            errors.append(
                f"Project slug mismatch for ZIP: folder={project_dir.name} zip={parsed.project_slug} file={rel}"
            )
            invalid_zip_paths.append(rel)
            continue

        valid_zips.append(
            {
                "sequence": parsed.sequence,
                "project_slug": parsed.project_slug,
                "package_slug": parsed.package_slug,
                "zip_name": entry.name,
                "relative_path": rel,
                "absolute_path": str(entry.resolve()),
            }
        )

    valid_zips.sort(key=lambda item: (item["sequence"], item["zip_name"].lower()))
    sequences = [item["sequence"] for item in valid_zips]
    seq_status = sequence_status_from_values(sequences)

    if seq_status["duplicate_sequences"]:
        errors.append(
            "Duplicate sequence numbers: "
            + ", ".join(str(value) for value in seq_status["duplicate_sequences"])
        )
    if seq_status["missing_sequences"]:
        errors.append(
            "Sequence gaps detected: "
            + ", ".join(str(value) for value in seq_status["missing_sequences"])
        )

    return {
        "project_slug": project_dir.name,
        "valid": len(errors) == 0,
        "zip_count": len(valid_zips),
        "sequence_status": seq_status,
        "errors": errors,
        "warnings": warnings,
        "valid_zips": valid_zips,
        "invalid_zip_paths": sorted(set(invalid_zip_paths)),
    }


def build_validation_report(inbox_root: Path, project_slug: str | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not inbox_root.exists():
        errors.append(f"Inbox root does not exist: {inbox_root}")
        projects: list[dict] = []
    elif not inbox_root.is_dir():
        errors.append(f"Inbox root is not a directory: {inbox_root}")
        projects = []
    else:
        projects = [_project_validation(project_dir, inbox_root) for project_dir in collect_project_dirs(inbox_root, project_slug)]

    if project_slug and not projects and not errors:
        errors.append(f"Project inbox folder not found: {project_slug}")

    global_invalid_paths = sorted(
        {
            invalid
            for project in projects
            for invalid in project.get("invalid_zip_paths", [])
        }
    )

    error_count = len(errors) + sum(len(project["errors"]) for project in projects)
    warning_count = len(warnings) + sum(len(project["warnings"]) for project in projects)
    zip_count = sum(project["zip_count"] for project in projects)

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "inbox_root": str(inbox_root),
        "project_filter": project_slug,
        "valid": error_count == 0,
        "summary": {
            "project_count": len(projects),
            "zip_count": zip_count,
            "error_count": error_count,
            "warning_count": warning_count,
        },
        "errors": errors,
        "warnings": warnings,
        "projects": projects,
        "invalid_zip_paths": global_invalid_paths,
    }


def main() -> int:
    parser = default_arg_parser("Validate ZIP inbox naming and sequencing")
    parser.add_argument("--project", help="Optional project slug filter")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = repo_root_from_arg(args.repo_root)
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    report = build_validation_report(inbox_root, args.project)
    write_json(Path(args.output), report)

    print("STATUS:", "PASS" if report["valid"] else "FAIL")
    print(f"projects: {report['summary']['project_count']}")
    print(f"zip_count: {report['summary']['zip_count']}")
    print(f"errors: {report['summary']['error_count']}")
    print(f"warnings: {report['summary']['warning_count']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
