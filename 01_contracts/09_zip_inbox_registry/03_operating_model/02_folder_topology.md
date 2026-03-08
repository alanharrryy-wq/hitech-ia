# Folder Topology

## Canonical intake tree

```text
<contract-repo>/
  02_modules/
    _zip_inbox/
      <project_slug>/
        zip1_<project_slug>_<package_slug>.zip
        zip2_<project_slug>_<package_slug>.zip
        zip3_<project_slug>_<package_slug>.zip
        project.manifest.json
        _processed/
        _failed/
        _staging/
```

## Meaning of folders

- `_zip_inbox/` : immutable source drop area for incoming ZIP packages
- `<project_slug>/` : isolated intake queue for one project
- `_processed/` : ZIPs successfully consumed and archived
- `_failed/` : ZIPs that failed validation or apply and must be reviewed
- `_staging/` : temporary extraction area ignored by version control

## Recommended neighboring folders in the contract repo

```text
<contract-repo>/
  01_contracts/
  02_modules/
  03_prompts/
  04_runs/zip_inbox/
  05_reports/zip_inbox/
  06_scripts/
  07_templates/
  08_schemas/
  09_examples/
```
