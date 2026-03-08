# ZIP Inbox Contract

## 1. Intake Root
Artifacts arrive in:

`02_modules/_zip_inbox/<project_slug>/`

Each project has its own folder. Cross-project packages are invalid.

## 2. ZIP Naming
Allowed filename pattern:

`zip<sequence>_<project_slug>_<package_slug>.zip`

Examples:
- `zip1_ui_observability_core.zip`
- `zip2_ui_observability_rules_reporting.zip`

## 3. Sequence Rules
- Sequence starts at 1 for a new project inbox.
- Sequences must be contiguous.
- Gaps are blocking errors.
- Duplicates are blocking errors.
- Sorting is numeric, not lexical.

## 4. Lifecycle States
Registry should support at least:

- `pending`
- `validated`
- `planned`
- `applied`
- `processed`
- `failed`
- `quarantined`

## 5. Safety Rules
A ZIP must be quarantined if any of the following occurs:
- Invalid filename
- Project slug mismatch
- Missing manifest
- Invalid manifest schema
- Illegal extraction path (`..`, absolute paths, drive roots)
- Duplicate package intent with conflicting sequence/hash
- Unsafe overwrite attempt outside allowed destinations

## 6. Full Cycle
Expected high-level flow:

1. Scan inbox
2. Validate naming and sequence
3. Build registry snapshot
4. Create install plan
5. Acquire lock
6. Extract each ZIP into staging
7. Read manifest
8. Route/copy files into repo targets
9. Run tests
10. Write report
11. Archive processed ZIPs
12. Update registry final state

## 7. Determinism
For same input ZIP set + same repo state:
- plan order must be stable
- registry output must be stable
- report schema must be stable
- archive location format must be stable

## 8. Locking
UniCodex should implement a real lock for the full cycle. Minimum acceptable options:
- file lock
- PID lock
- OS mutex

Lock file recommendation:

`.install.lock`

The system must refuse concurrent application runs.

## 9. Quarantine
Quarantined artifacts must be moved into a deterministic project-scoped quarantine path and referenced in reports.
