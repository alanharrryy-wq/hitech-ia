# Report Schema

A full cycle run should emit one machine-readable report and optionally one human-readable summary.

## Recommended locations
- `05_reports/zip_inbox/<project_slug>/<run_id>/report.json`
- `05_reports/zip_inbox/<project_slug>/<run_id>/summary.md`

## JSON Schema (practical contract)
```json
{
  "schema_version": "1.0",
  "run_id": "20260307T120000Z_ui_observability",
  "project_slug": "ui_observability",
  "started_at": "2026-03-07T12:00:00Z",
  "finished_at": "2026-03-07T12:03:10Z",
  "status": "success",
  "validated_sequences": [1, 2],
  "applied_packages": ["core", "rules_reporting"],
  "quarantined_packages": [],
  "failed_packages": [],
  "tests": [],
  "operations": [],
  "summary": {
    "zip_count": 2,
    "applied_count": 2,
    "failed_count": 0,
    "quarantined_count": 0
  }
}
```

## Status values
- `success`
- `partial_failure`
- `failure`

## `tests` entries
Each test record should include:
- `name`
- `type`
- `command`
- `started_at`
- `finished_at`
- `exit_code`
- `required`
- `status`
- `stdout_path`
- `stderr_path`

## `operations` entries
Each operation record should include:
- `package_slug`
- `source`
- `destination`
- `action`
- `result`
- `duration_ms`

## Summary markdown
Human summary should state:
- what was found
- what was applied
- what failed
- where logs and backups are
