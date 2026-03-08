# Archive Policy

## Objective
Move successfully processed ZIPs out of inbox into deterministic archive storage.

## Processed Archive Location
Recommended path:

`02_modules/_zip_archive/<project_slug>/<yyyy>/<mm>/<dd>/`

Example:
`02_modules/_zip_archive/ui_observability/2026/03/07/zip1_ui_observability_core.zip`

## Quarantine Location
Recommended path:

`02_modules/_zip_quarantine/<project_slug>/<yyyy>/<mm>/<dd>/`

## Rules
- Only `processed` artifacts go to archive
- Invalid or unsafe artifacts go to quarantine
- Failed apply/test artifacts remain traceable and should either stay in inbox with failure marker or move to quarantine according to policy

## Atomicity Recommendation
Do not move files one by one without state protection.
Preferred flow:
1. mark intent
2. move to temp archive path
3. verify existence + checksum if needed
4. finalize registry/report state

## Duplicate Archive Rule
If archive destination already exists:
- compare checksum
- if identical, do not duplicate blindly
- if different, mark severe conflict and stop

## Archive Metadata
Archive action should record:
- original path
- final path
- moved_at
- checksum
- run_id
