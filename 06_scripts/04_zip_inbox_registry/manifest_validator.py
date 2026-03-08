from __future__ import annotations

import json
from pathlib import Path

from common import (
    SUPPORTED_TARGET_MODES,
    SUPPORTED_TEST_TYPES,
    SUPPORTED_WIRING_MODES,
    ValidationError,
    ZipArtifact,
    manifest_candidate_paths,
    resolve_repo_destination,
    resolve_safe_relative_path,
)

ALLOWED_KINDS = {"module", "config", "assets", "tests", "docs", "mixed"}
REQUIRED_FIELDS = {
    "schema_version",
    "project_slug",
    "package_slug",
    "sequence",
    "package_version",
    "kind",
    "wiring_mode",
    "targets",
    "tests",
}


def load_manifest_from_extracted(package_root: Path) -> tuple[dict, str]:
    for relative in manifest_candidate_paths():
        manifest_path = package_root / relative
        if manifest_path.exists() and manifest_path.is_file():
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid manifest JSON at {relative}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValidationError(f"Manifest root must be an object at {relative}")
            return payload, relative
    raise ValidationError("Missing manifest.json (or .hitech/manifest.json)")


def _validate_required_fields(manifest: dict) -> None:
    missing = sorted(REQUIRED_FIELDS - set(manifest))
    if missing:
        raise ValidationError("Manifest missing required fields: " + ", ".join(missing))


def _normalize_target(
    target: dict,
    *,
    index: int,
    extracted_root: Path,
    repo_root: Path,
) -> dict:
    if not isinstance(target, dict):
        raise ValidationError(f"targets[{index}] must be an object")

    if "source" not in target or "destination" not in target:
        raise ValidationError(f"targets[{index}] requires source and destination")

    source_rel = resolve_safe_relative_path(str(target["source"]))
    destination_rel = resolve_safe_relative_path(str(target["destination"]))

    mode = str(target.get("mode", "overwrite"))
    if mode not in SUPPORTED_TARGET_MODES:
        raise ValidationError(f"targets[{index}] unsupported mode: {mode}")

    required = bool(target.get("required", True))
    source_path = (extracted_root / source_rel).resolve()
    try:
        source_path.relative_to(extracted_root)
    except ValueError as exc:
        raise ValidationError(f"targets[{index}] source escapes extraction root: {source_rel}") from exc

    # Destination safety and policy check.
    resolve_repo_destination(repo_root, destination_rel)

    if not source_path.exists() and required:
        raise ValidationError(f"targets[{index}] required source missing: {source_rel}")

    return {
        "source": source_rel,
        "destination": destination_rel,
        "mode": mode,
        "required": required,
    }


def _normalize_test(test: dict, *, index: int) -> dict:
    if not isinstance(test, dict):
        raise ValidationError(f"tests[{index}] must be an object")

    test_type = str(test.get("type", "command"))
    if test_type not in SUPPORTED_TEST_TYPES:
        raise ValidationError(f"tests[{index}] unsupported type: {test_type}")

    command = str(test.get("command", "")).strip()
    if not command:
        raise ValidationError(f"tests[{index}] command is required")

    name = str(test.get("name", f"test_{index + 1}"))
    required = bool(test.get("required", True))

    return {
        "name": name,
        "type": test_type,
        "command": command,
        "required": required,
    }


def validate_and_normalize_manifest(
    manifest: dict,
    *,
    artifact: ZipArtifact,
    extracted_root: Path,
    repo_root: Path,
) -> dict:
    _validate_required_fields(manifest)

    schema_version = str(manifest["schema_version"])
    project_slug = str(manifest["project_slug"])
    package_slug = str(manifest["package_slug"])

    if project_slug != artifact.project_slug:
        raise ValidationError(
            f"Manifest project_slug mismatch: manifest={project_slug} zip={artifact.project_slug}"
        )
    if package_slug != artifact.package_slug:
        raise ValidationError(
            f"Manifest package_slug mismatch: manifest={package_slug} zip={artifact.package_slug}"
        )

    try:
        sequence = int(manifest["sequence"])
    except (TypeError, ValueError) as exc:
        raise ValidationError("Manifest sequence must be an integer") from exc

    if sequence != artifact.sequence:
        raise ValidationError(f"Manifest sequence mismatch: manifest={sequence} zip={artifact.sequence}")

    package_version = str(manifest["package_version"]).strip()
    if not package_version:
        raise ValidationError("Manifest package_version must be a non-empty string")

    kind = str(manifest["kind"])
    if kind not in ALLOWED_KINDS:
        raise ValidationError(f"Manifest kind unsupported: {kind}")

    wiring_mode = str(manifest["wiring_mode"])
    if wiring_mode not in SUPPORTED_WIRING_MODES:
        raise ValidationError(
            f"Manifest wiring_mode unsupported by MVP policy: {wiring_mode}. Allowed: {sorted(SUPPORTED_WIRING_MODES)}"
        )

    targets_payload = manifest.get("targets", [])
    if not isinstance(targets_payload, list):
        raise ValidationError("Manifest targets must be an array")

    normalized_targets = [
        _normalize_target(target, index=index, extracted_root=extracted_root, repo_root=repo_root)
        for index, target in enumerate(targets_payload)
    ]

    destinations = [entry["destination"] for entry in normalized_targets]
    duplicate_destinations = sorted({item for item in destinations if destinations.count(item) > 1})
    if duplicate_destinations:
        raise ValidationError("Manifest has duplicate destinations: " + ", ".join(duplicate_destinations))

    tests_payload = manifest.get("tests", [])
    if not isinstance(tests_payload, list):
        raise ValidationError("Manifest tests must be an array")
    normalized_tests = [_normalize_test(test, index=index) for index, test in enumerate(tests_payload)]

    return {
        "schema_version": schema_version,
        "project_slug": project_slug,
        "package_slug": package_slug,
        "sequence": sequence,
        "package_version": package_version,
        "kind": kind,
        "wiring_mode": wiring_mode,
        "targets": normalized_targets,
        "tests": normalized_tests,
        "depends_on": manifest.get("depends_on", []),
        "notes": manifest.get("notes", ""),
    }
