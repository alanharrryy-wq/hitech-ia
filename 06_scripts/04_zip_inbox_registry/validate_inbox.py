from __future__ import annotations

from pathlib import Path

from common import (
    ALLOWED_PROJECT_INTERNAL_DIRS,
    ALLOWED_PROJECT_NON_ZIP_FILES,
    default_arg_parser,
    normalize,
    parse_zip_name,
    resolve_inbox_root,
    sequence_status_from_values,
    utc_now,
    write_json,
)


def _project_report(project_dir: Path, inbox_root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    packages: list[dict] = []
    manifest_present = False

    for entry in sorted(project_dir.iterdir(), key=lambda item: item.name.lower()):
        rel = normalize(entry.relative_to(inbox_root))
        if entry.is_dir():
            if entry.name in ALLOWED_PROJECT_INTERNAL_DIRS:
                continue
            if entry.name.startswith("_"):
                warnings.append(f"Reserved directory is not recognized: {rel}")
                continue
            errors.append(f"Unexpected directory in project inbox: {rel}")
            continue

        if entry.name == "project.manifest.json":
            manifest_present = True
            continue

        if entry.name in ALLOWED_PROJECT_NON_ZIP_FILES:
            continue

        if entry.suffix.lower() != ".zip":
            warnings.append(f"Unexpected non-ZIP file in project inbox: {rel}")
            continue

        parsed = parse_zip_name(entry.name)
        if not parsed:
            errors.append(f"Invalid ZIP filename: {rel}")
            continue

        sequence = int(parsed["sequence"])
        project_slug = str(parsed["project_slug"])
        package_slug = str(parsed["package_slug"])
        if project_slug != project_dir.name:
            errors.append(
                "Project folder and ZIP project slug mismatch: "
                f"folder={project_dir.name} zip={project_slug} file={rel}"
            )
            continue

        packages.append(
            {
                "filename": entry.name,
                "sequence": sequence,
                "project_slug": project_slug,
                "package_slug": package_slug,
                "relative_path": rel,
            }
        )

    sequences = [package["sequence"] for package in packages]
    seq_status = sequence_status_from_values(sequences)
    if seq_status["duplicate_sequences"]:
        errors.append(
            "Duplicate sequences detected: "
            + ", ".join(str(value) for value in seq_status["duplicate_sequences"])
        )
    if seq_status["missing_sequences"]:
        errors.append(
            "Missing sequences detected: "
            + ", ".join(str(value) for value in seq_status["missing_sequences"])
        )

    packages.sort(key=lambda package: (package["sequence"], package["filename"].lower()))

    return {
        "project_slug": project_dir.name,
        "folder": normalize(project_dir.relative_to(inbox_root)),
        "manifest_present": manifest_present,
        "zip_count": len(packages),
        "sequence_status": seq_status,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "packages": packages,
    }


def build_validation_report(inbox_root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    projects: list[dict] = []
    allowed_root_files = {"00_README.md", "README.md", ".gitkeep"}

    if not inbox_root.exists():
        errors.append(f"Inbox root does not exist: {inbox_root}")
    elif not inbox_root.is_dir():
        errors.append(f"Inbox root is not a directory: {inbox_root}")
    else:
        for child in sorted(inbox_root.iterdir(), key=lambda item: item.name.lower()):
            rel = normalize(child.relative_to(inbox_root))
            if child.is_file():
                if child.name in allowed_root_files:
                    continue
                if child.suffix.lower() == ".zip":
                    errors.append(f"ZIP found in inbox root; expected project folder isolation: {rel}")
                else:
                    warnings.append(f"Unexpected file in inbox root: {rel}")
                continue
            if child.name.startswith("_"):
                continue
            projects.append(_project_report(child, inbox_root))

    invalid_zip_files: list[str] = []
    for project in projects:
        for message in project["errors"]:
            if message.startswith("Invalid ZIP filename:"):
                invalid_zip_files.append(message.split(": ", 1)[1])

    project_error_count = sum(len(project["errors"]) for project in projects)
    project_warning_count = sum(len(project["warnings"]) for project in projects)
    zip_count = sum(project["zip_count"] for project in projects)

    generated_at = utc_now()
    return {
        "validation_schema_version": "1.1.0",
        "generated_at": generated_at,
        "generated_at_utc": generated_at,
        "inbox_root": str(inbox_root),
        "valid": len(errors) == 0 and project_error_count == 0,
        "summary": {
            "project_count": len(projects),
            "zip_count": zip_count,
            "error_count": len(errors) + project_error_count,
            "warning_count": len(warnings) + project_warning_count,
        },
        "errors": errors,
        "warnings": warnings,
        "projects_detected": sorted(project["project_slug"] for project in projects),
        "projects": projects,
        "invalid_zip_files": sorted(set(invalid_zip_files)),
    }


def main() -> int:
    parser = default_arg_parser("Validate ZIP inbox naming, ordering, and project isolation")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    inbox_root = resolve_inbox_root(repo_root, args.inbox_root)

    report = build_validation_report(inbox_root)
    write_json(Path(args.output), report)

    print("STATUS:", "PASS" if report["valid"] else "FAIL")
    print(f"projects: {report['summary']['project_count']}")
    print(f"zip_count: {report['summary']['zip_count']}")
    print(f"errors: {report['summary']['error_count']}")
    print(f"warnings: {report['summary']['warning_count']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
