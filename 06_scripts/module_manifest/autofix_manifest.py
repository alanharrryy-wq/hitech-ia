from __future__ import annotations

from copy import deepcopy

from test_policy_normalizer import normalize_relative_path, normalize_tests, validate_slug

ALLOWED_KINDS = {"module", "config", "assets", "tests", "docs", "mixed"}
ALLOWED_WIRING_MODES = {"copy", "merge"}
ALLOWED_TARGET_MODES = {"overwrite", "create_only", "skip_if_exists", "fail_if_exists"}

def _normalize_target(target: dict, index: int) -> tuple[dict, list[str]]:
    if not isinstance(target, dict):
        raise ValueError(f"targets[{index}] must be an object")
    if "source" not in target or "destination" not in target:
        raise ValueError(f"targets[{index}] requires source and destination")

    warnings: list[str] = []
    normalized = {
        "source": normalize_relative_path(str(target["source"])),
        "destination": normalize_relative_path(str(target["destination"])),
        "mode": str(target.get("mode", "overwrite")),
        "required": bool(target.get("required", True)),
    }
    if "mode" not in target:
        warnings.append("default_target_mode_applied")
    if "required" not in target:
        warnings.append("default_target_required_applied")
    if normalized["mode"] not in ALLOWED_TARGET_MODES:
        raise ValueError(f"targets[{index}] unsupported mode: {normalized['mode']}")
    return normalized, warnings

def autofix_manifest(existing_manifest: dict | None, inference_report: dict) -> tuple[dict, dict, list[str]]:
    warnings: list[str] = []
    base = deepcopy(existing_manifest) if isinstance(existing_manifest, dict) else {}

    project_slug = validate_slug(
        str(base.get("project_slug") or inference_report["probable_project_slug"]),
        "project_slug",
    )
    package_slug = validate_slug(
        str(base.get("package_slug") or inference_report["probable_package_slug"]),
        "package_slug",
    )

    sequence_source = (
        base.get("sequence")
        if base.get("sequence") not in (None, "", 0)
        else inference_report["project_resolution"]["tentative_sequence"]
    )
    try:
        sequence = int(sequence_source)
    except Exception as exc:
        raise ValueError("sequence must be an integer") from exc
    if sequence < 1:
        raise ValueError("sequence must be >= 1")

    package_version = str(base.get("package_version") or "0.1.0").strip() or "0.1.0"
    kind = str(base.get("kind") or "module")
    if kind not in ALLOWED_KINDS:
        warnings.append("kind_reset_to_module")
        kind = "module"

    wiring_mode = str(base.get("wiring_mode") or "copy")
    if wiring_mode not in ALLOWED_WIRING_MODES:
        warnings.append("wiring_mode_reset_to_copy")
        wiring_mode = "copy"

    target_source = base.get("targets")
    if not isinstance(target_source, list) or not target_source:
        target_source = inference_report.get("target_suggestions", [])
        warnings.append("targets_seeded_from_inference")
    normalized_targets = []
    for index, target in enumerate(target_source):
        item, item_warnings = _normalize_target(target, index)
        normalized_targets.append(item)
        warnings.extend(item_warnings)
    normalized_targets.sort(key=lambda item: (item["destination"].lower(), item["source"].lower()))

    tests_source = base.get("tests", [])
    normalized_tests, test_warnings = normalize_tests(tests_source)
    warnings.extend(test_warnings)

    depends_on = base.get("depends_on", [])
    if depends_on is None:
        depends_on = []
    if not isinstance(depends_on, list):
        raise ValueError("depends_on must be an array")

    notes = str(base.get("notes", ""))

    manifest = {
        "schema_version": "1.0",
        "project_slug": project_slug,
        "package_slug": package_slug,
        "sequence": sequence,
        "package_version": package_version,
        "kind": kind,
        "wiring_mode": wiring_mode,
        "targets": normalized_targets,
        "tests": normalized_tests,
        "depends_on": depends_on,
        "notes": notes,
    }

    metadata = {
        "project_slug_from_inference": inference_report["probable_project_slug"],
        "package_slug_from_inference": inference_report["probable_package_slug"],
        "tentative_sequence_from_inference": inference_report["project_resolution"]["tentative_sequence"],
    }

    return manifest, metadata, sorted(set(warnings))
