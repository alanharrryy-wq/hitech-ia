# ZIP Inbox Landing Zone

`02_modules/_zip_inbox/` is the canonical landing zone for all incoming ZIP deliveries.

## Canonical filename

`zip<sequence>_<project_slug>_<package_slug>.zip`

Example:
- `zip4_ui_observability_ai_agent.zip`

## Required operating model

1. Create one folder per project slug under `_zip_inbox/`.
2. Download ZIP files directly into that project folder.
3. Do not place ZIP files in the `_zip_inbox/` root.
4. Keep ZIP files immutable after download.
5. Process ZIP files by numeric sequence (`zip1`, `zip2`, `zip3`, ...).
6. Never mix ZIP files from different project slugs in one project folder.

## Project folder structure

```text
02_modules/_zip_inbox/<project_slug>/
  zip1_<project_slug>_<package_slug>.zip
  zip2_<project_slug>_<package_slug>.zip
  project.manifest.json  (optional)
  _processed/
  _failed/
  _staging/
```

## Execution entrypoint

Use:

`06_scripts/04_zip_inbox_registry/run_full_cycle.py`

Outputs are written to:
- `04_runs/zip_inbox/`
- `05_reports/zip_inbox/`

## Template

Use `_project_template/` in this folder as a neutral starter.
