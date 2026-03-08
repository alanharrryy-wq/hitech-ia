# ZIP Inbox Runtime

Deterministic ZIP inbox automation runtime.

## One-command entrypoint

```bash
python run_full_cycle.py --project <project_slug>
```

## Full lifecycle

`validate -> registry -> plan -> extract -> wiring -> tests -> report -> archive/quarantine`

## Safety controls

- global lock via `.install.lock`
- ZIP path traversal blocking
- absolute path blocking
- repo-bound destination enforcement
- dry-run operation planning before writes
- rollback for current package on wiring/test failure
- deterministic archive and quarantine paths

## Key scripts

- `run_full_cycle.py` (repo root wrapper)
- `06_scripts/04_zip_inbox_registry/run_full_cycle.py`
- `06_scripts/04_zip_inbox_registry/validate_inbox.py`
- `06_scripts/04_zip_inbox_registry/build_registry.py`
- `06_scripts/04_zip_inbox_registry/make_install_plan.py`
- `06_scripts/04_zip_inbox_registry/archive_processed.py`
- `06_scripts/04_zip_inbox_registry/apply_archive_policy.py`

## Output paths

- staging: `04_runs/zip_inbox/<run_id>/staging/`
- logs: `04_runs/zip_inbox/<run_id>/logs/`
- backups: `04_runs/zip_inbox/<run_id>/backups/`
- report: `05_reports/zip_inbox/<project_slug>/<run_id>/report.json`
- summary: `05_reports/zip_inbox/<project_slug>/<run_id>/summary.md`
- archive: `02_modules/_zip_archive/<project_slug>/<yyyy>/<mm>/<dd>/`
- quarantine: `02_modules/_zip_quarantine/<project_slug>/<yyyy>/<mm>/<dd>/`

## Test suite

```bash
python -m unittest discover -s 06_scripts/04_zip_inbox_registry/tests -v
```
