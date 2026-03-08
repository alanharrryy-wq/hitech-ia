# Merge Resolution: Reference Pack + Runtime Pack

This repository installs both ZIP packs as one coherent neutral subsystem.

## Conflict resolution

1. Duplicate overview docs (`README_FIRST`, `SYSTEM_MAP`)
- Resolution: reference pack docs are canonical under this contract folder.
- Runtime pack docs are preserved in `13_runtime_docs/` as implementation context.

2. Duplicate registry/install-plan schemas across packs
- Resolution: reference pack schemas are canonical in `08_schemas/06_zip_inbox_registry/`.
- Runtime-specific validation report schema is retained as `09_validation_report.schema.json`.

3. Duplicate example domains across packs
- Resolution: reference examples are canonical in `09_examples/06_zip_inbox_registry/`.
- Runtime validation report example is retained as `09_validation_report.example.json`.

4. Reference scripts vs runtime scripts
- Resolution: runtime scripts are installed as executable scripts in `06_scripts/04_zip_inbox_registry/`.
- Reference scripts are retained in this contract folder as design references.

5. Runtime pack compiled caches (`__pycache__/*.pyc`)
- Resolution: excluded from installation because they are environment-specific artifacts.

## Canonical standards after merge

- Landing zone: `02_modules/_zip_inbox/`
- Filename pattern: `zip<sequence>_<project_slug>_<package_slug>.zip`
- Ordering: numeric sequence parsing (`zip10` comes after `zip9`)
- Project isolation: one project slug per folder
- Registry/plan outputs: deterministic JSON in `04_runs/zip_inbox/`
- Reports: deterministic markdown in `05_reports/zip_inbox/`
