# Installed Runtime Commands

## Validate inbox

```bash
python 06_scripts/04_zip_inbox_registry/validate_inbox.py \
  --repo-root . \
  --output 04_runs/zip_inbox/validation_report.json
```

## Build internal registry

```bash
python 06_scripts/04_zip_inbox_registry/build_registry.py \
  --repo-root . \
  --output 04_runs/zip_inbox/registry_snapshot.json
```

## Generate install plan for one project

```bash
python 06_scripts/04_zip_inbox_registry/make_install_plan.py \
  --repo-root . \
  --project-slug <project_slug> \
  --output 04_runs/zip_inbox/install_plan_<project_slug>.json
```

## Archive processed ZIP packages

```bash
python 06_scripts/04_zip_inbox_registry/archive_processed.py \
  --repo-root . \
  --project-slug <project_slug> \
  --output 04_runs/zip_inbox/archive_manifest_<project_slug>.json
```

## Archive failed ZIP packages

```bash
python 06_scripts/04_zip_inbox_registry/apply_archive_policy.py \
  --repo-root . \
  --project-slug <project_slug> \
  --target failed \
  --output 04_runs/zip_inbox/archive_failed_<project_slug>.json
```

## Full-cycle dry run

```bash
python 06_scripts/04_zip_inbox_registry/run_full_cycle.py \
  --repo-root . \
  --project-slug <project_slug> \
  --mode dry_run
```

## Full-cycle apply run

```bash
python 06_scripts/04_zip_inbox_registry/run_full_cycle.py \
  --repo-root . \
  --project-slug <project_slug> \
  --mode apply
```

## Validate schema/example integrity

```bash
python 06_scripts/04_zip_inbox_registry/validate_json_assets.py \
  --repo-root . \
  --output 04_runs/zip_inbox/schema_validation_report.json
```
