# Runbook

## Purpose
Operational guide for humans and UniCodex.

## One-command target
UniCodex should leave behind one command equivalent to:

`python run_full_cycle.py --project <project_slug>`

or repository-specific wrapper that does the same.

## Expected Runtime Flow
1. acquire lock
2. validate inbox
3. build registry
4. create install plan
5. apply packages in sequence order
6. run required tests
7. write report
8. archive/quarantine
9. release lock

## Preconditions
- repo root resolved
- project inbox exists
- permissions OK
- temp/staging directories creatable
- test toolchain available

## Outputs
- registry snapshot
- install plan
- report json
- human summary
- logs
- backups if writes occurred

## Operational Logs
Recommended paths:
- `04_runs/zip_inbox/<run_id>/logs/`
- `05_reports/zip_inbox/<project_slug>/<run_id>/`

## Exit Codes
Suggested:
- `0` success
- `1` validation failure
- `2` apply failure
- `3` test failure
- `4` lock failure
- `5` archive/quarantine finalization failure
