# System Map

## Core directories

- `02_modules/_zip_inbox/`
  - incoming ZIP packages by project slug
- `04_runs/zip_inbox/`
  - machine-readable run outputs
- `05_reports/zip_inbox/`
  - human-readable reports
- `06_scripts/`
  - deterministic automation scripts (`06_scripts/04_zip_inbox_registry/`)
- `08_schemas/`
  - JSON schemas for registry and plan outputs
- `09_examples/`
  - valid example files

## High-level flow

1. ZIP packages arrive in `_zip_inbox`
2. `validate_inbox.py` checks naming and structure assumptions
3. `build_registry.py` produces a complete registry snapshot
4. `make_install_plan.py` creates a project-specific installation plan
5. external automation performs extraction and file routing
6. `archive_processed.py` archives completed ZIPs
7. updated reports and registry snapshots are persisted

## Internal registry roles

The registry exists to answer these questions deterministically:
- which project slugs exist,
- which ZIP sequence numbers are present,
- whether a sequence is continuous,
- which ZIPs are pending,
- which ZIPs are archived,
- whether duplicates or naming conflicts exist.
