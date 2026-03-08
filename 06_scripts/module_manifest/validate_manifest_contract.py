from __future__ import annotations

import argparse
import json
from pathlib import Path

from test_policy_normalizer import normalize_relative_path, validate_slug
from autofix_manifest import ALLOWED_KINDS, ALLOWED_WIRING_MODES, ALLOWED_TARGET_MODES

def validate_manifest_contract(manifest: dict) -> list[str]:
    errors: list[str] = []
    required_fields = {
        "schema_version", "project_slug", "package_slug", "sequence",
        "package_version", "kind", "wiring_mode", "targets", "tests"
    }
    missing = sorted(required_fields - set(manifest))
    if missing:
        errors.append("Missing required fields: " + ", ".join(missing))
        return errors

    try:
        validate_slug(str(manifest["project_slug"]), "project_slug")
    except Exception as exc:
        errors.append(str(exc))
    try:
        validate_slug(str(manifest["package_slug"]), "package_slug")
    except Exception as exc:
        errors.append(str(exc))

    try:
        sequence = int(manifest["sequence"])
        if sequence < 1:
            errors.append("sequence must be >= 1")
    except Exception:
        errors.append("sequence must be an integer")

    if str(manifest["kind"]) not in ALLOWED_KINDS:
        errors.append(f"Unsupported kind: {manifest['kind']}")
    if str(manifest["wiring_mode"]) not in ALLOWED_WIRING_MODES:
        errors.append(f"Unsupported wiring_mode: {manifest['wiring_mode']}")

    targets = manifest.get("targets")
    if not isinstance(targets, list):
        errors.append("targets must be an array")
    else:
        seen_destinations: set[str] = set()
        for index, target in enumerate(targets):
            if not isinstance(target, dict):
                errors.append(f"targets[{index}] must be an object")
                continue
            if "source" not in target or "destination" not in target:
                errors.append(f"targets[{index}] requires source and destination")
                continue
            try:
                source = normalize_relative_path(str(target["source"]))
                destination = normalize_relative_path(str(target["destination"]))
            except Exception as exc:
                errors.append(f"targets[{index}] {exc}")
                continue
            mode = str(target.get("mode", "overwrite"))
            if mode not in ALLOWED_TARGET_MODES:
                errors.append(f"targets[{index}] unsupported mode: {mode}")
            if destination in seen_destinations:
                errors.append(f"Duplicate destination: {destination}")
            seen_destinations.add(destination)

    tests = manifest.get("tests")
    if not isinstance(tests, list):
        errors.append("tests must be an array")
    else:
        for index, test in enumerate(tests):
            if not isinstance(test, dict):
                errors.append(f"tests[{index}] must be an object")
                continue
            if str(test.get("type", "")).lower() != "command":
                errors.append(f"tests[{index}] unsupported type")
            args = test.get("args")
            if not isinstance(args, list) or not args:
                errors.append(f"tests[{index}] args must be a non-empty array")
            cwd = test.get("cwd")
            if cwd:
                try:
                    normalize_relative_path(str(cwd))
                except Exception as exc:
                    errors.append(f"tests[{index}] cwd {exc}")

    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manifest contract")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate_manifest_contract(manifest)
    print("STATUS:", "PASS" if not errors else "FAIL")
    if errors:
        for error in errors:
            print(error)
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
