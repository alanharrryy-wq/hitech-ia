# 02 Repo Layout Contract

## Root contract
The repository root must contain only:
- `00_README.md`
- `.gitignore`
- numbered top-level folders defined by the master contract
- optional repo metadata files such as `LICENSE` or `.gitattributes`

## Folder roles
### `01_contracts/`
Laws, contracts, acceptance rules, decision logs, migration notes.

### `02_modules/`
Installable ZIP artifacts grouped by domain. This is the operational payload shelf.
`02_modules/_zip_inbox/` is the canonical landing zone for future ZIP deliveries using:
`zip<sequence>_<project_slug>_<package_slug>.zip`.

### `03_prompts/`
Codex installer prompts, worker prompts, and prompt references.

### `04_runs/`
Historical execution folders, staged by year or topic, containing reports and receipts.

### `05_reports/`
Human-oriented summaries, adoption notes, and health reports.

### `06_scripts/`
Validation, unpacking helpers, and deterministic repo tooling.

### `07_templates/`
Scaffolds for new modules, prompts, and contract packs.

### `08_schemas/`
JSON Schemas for manifests, reports, and prompt requests.

### `09_examples/`
Example manifests and reference payloads that validate against the schemas.

### `99_legacy_archive/`
Optional quarantine zone for old repo content that was intentionally retained during migration.

## Prohibited roots
Do not create ad-hoc roots such as `misc/`, `tmp/`, `old/`, or `stuff/`.

## Stability rule
Adding a new top-level numbered folder requires:
1. master contract update,
2. decision log entry,
3. validator update,
4. README root layout update.
