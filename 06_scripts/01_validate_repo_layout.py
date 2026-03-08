#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROOTS = [
    '01_contracts',
    '02_modules',
    '03_prompts',
    '04_runs',
    '05_reports',
    '06_scripts',
    '07_templates',
    '08_schemas',
    '09_examples',
]
SCHEMA_EXAMPLES = [
    ('08_schemas/01_repo_contract.schema.json', '09_examples/01_repo_contract.example.json'),
    ('08_schemas/02_module_manifest.schema.json', '09_examples/02_module_manifest.example.json'),
    ('08_schemas/03_zip_package_manifest.schema.json', '09_examples/03_zip_package_manifest.example.json'),
    ('08_schemas/04_codex_install_request.schema.json', '09_examples/04_codex_install_request.example.json'),
    ('08_schemas/05_run_report.schema.json', '09_examples/05_run_report.example.json'),
]


def stable_print(lines: Iterable[str]) -> None:
    for line in lines:
        print(line)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def validate_required_roots(failures: list[str]) -> None:
    for name in REQUIRED_ROOTS:
        require((ROOT / name).is_dir(), f'missing required root: {name}', failures)


def validate_numbered_contracts(failures: list[str]) -> None:
    contracts = ROOT / '01_contracts'
    expected = [
        '01_master_contract.md',
        '02_repo_layout_contract.md',
        '03_zip_module_standard.md',
        '04_numbering_naming_contract.md',
        '05_codex_operating_contract.md',
        '06_acceptance_contract.md',
        '07_wiring_and_install_contract.md',
        '08_decision_log.md',
    ]
    for name in expected:
        require((contracts / name).is_file(), f'missing contract doc: {name}', failures)


def validate_basic_schema(schema: dict, example: dict, failures: list[str], label: str) -> None:
    required = schema.get('required', [])
    for key in required:
        require(key in example, f'{label}: missing required example field: {key}', failures)
    properties = schema.get('properties', {})
    for key in example.keys():
        require(key in properties or schema.get('additionalProperties', True), f'{label}: unexpected field in example: {key}', failures)


def validate_examples(failures: list[str]) -> None:
    for schema_rel, example_rel in SCHEMA_EXAMPLES:
        schema_path = ROOT / schema_rel
        example_path = ROOT / example_rel
        require(schema_path.is_file(), f'missing schema: {schema_rel}', failures)
        require(example_path.is_file(), f'missing example: {example_rel}', failures)
        if schema_path.is_file() and example_path.is_file():
            schema = load_json(schema_path)
            example = load_json(example_path)
            validate_basic_schema(schema, example, failures, example_rel)


def main() -> int:
    failures: list[str] = []
    validate_required_roots(failures)
    validate_numbered_contracts(failures)
    validate_examples(failures)

    if failures:
        stable_print(['STATUS: FAIL', *sorted(failures)])
        return 1
    stable_print([
        'STATUS: PASS',
        'layout_ok: true',
        'contracts_ok: true',
        'schemas_examples_ok: true',
        f'repo_root: {ROOT.as_posix()}',
    ])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
