# ZIP Inbox Registry Scripts

Deterministic runtime scripts for the neutral ZIP inbox control plane.

## Canonical naming

All installable ZIP files must follow:

`zip<sequence>_<project_slug>_<package_slug>.zip`

## Scripts

- `validate_inbox.py`
  - validates naming, folder isolation, duplicates, and sequence gaps
- `build_registry.py`
  - generates an internal registry with status, validation, eligibility, and archive state
- `make_install_plan.py`
  - generates a deterministic install plan for one project slug
- `archive_processed.py`
  - moves successfully processed ZIP files to `<project>/_processed/<run_id>/`
- `apply_archive_policy.py`
  - moves ZIP files to `<project>/_failed/<run_id>/` or `<project>/_quarantine/<run_id>/`
- `run_full_cycle.py`
  - executes validate -> registry -> plan -> optional archive -> post-registry
- `validate_json_assets.py`
  - validates JSON examples against JSON schemas

## Default paths

- inbox root: `02_modules/_zip_inbox/`
- run outputs: `04_runs/zip_inbox/`
- report outputs: `05_reports/zip_inbox/`

## Typical dry-run

```bash
python 06_scripts/04_zip_inbox_registry/run_full_cycle.py \
  --repo-root . \
  --project-slug sample_project \
  --mode dry_run
```

## Typical apply

```bash
python 06_scripts/04_zip_inbox_registry/run_full_cycle.py \
  --repo-root . \
  --project-slug sample_project \
  --mode apply
```
