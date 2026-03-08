# 01 Master Contract

## Scope
This contract governs the `hitech-ia` repository as an artifact and operations forge.

## Repository reason
Provide one stable place for:
- ZIP modules,
- implementation contracts,
- Codex prompts,
- schemas,
- reusable templates,
- run records,
- operator reports.

## Final goal
Turn repeatable installation and repo-shaping work into deterministic, documented, installable bundles so that Codex performs assembly, wiring, validation, and only minor conflict resolution.

## Hard laws
1. Product runtime code does not live here unless it is part of a module payload inside a package structure.
2. Every committed ZIP module must have a manifest, acceptance doc, wire plan, and installer prompt.
3. Every numbered folder must stay semantically stable across revisions.
4. Outputs written by local runs must be deterministic in ordering and naming.
5. Temporary unpack/output folders must be excluded from version control.
6. Schemas and examples must evolve together.
7. Changes that alter folder meaning require a decision-log entry.
8. Legacy content may be archived under `99_legacy_archive/` only with an archive note.

## Canonical root folders
- `01_contracts/`
- `02_modules/`
- `03_prompts/`
- `04_runs/`
- `05_reports/`
- `06_scripts/`
- `07_templates/`
- `08_schemas/`
- `09_examples/`

## Acceptance
A bootstrap is complete when the root layout exists, core docs exist, schemas validate, example files are present, and the validation script returns success.
