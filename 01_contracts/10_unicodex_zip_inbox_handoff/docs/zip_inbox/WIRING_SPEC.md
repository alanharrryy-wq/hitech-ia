# Wiring Specification

## Objective
Take extracted files from staging and place them into repository destinations safely and deterministically.

## Allowed Wiring Modes

### 1. copy
Direct copy from extracted artifact path to destination.

### 2. merge
Only for structured text or directories where merge semantics are explicitly implemented.
Do not guess merge behavior.

### 3. patch
Only if patch format and application engine are repository-approved.

### 4. scripted
Only if scripts are sandboxed, explicit and trusted.
Default policy: disabled.

## Recommended MVP
UniCodex should implement only:
- `copy`
- guarded `merge` for directories if clear rules exist

Everything else should fail closed.

## Destination Rules
- Destinations must be relative to repo root
- No absolute paths
- No parent traversal
- No writes outside project allowlist

## Overwrite Modes
Target entry may include:

- `overwrite`
- `create_only`
- `skip_if_exists`
- `fail_if_exists`

If omitted, default to `overwrite` only for explicitly targeted files.

## Staging Flow
For each ZIP:
1. Extract into temp path:
   - `04_runs/zip_inbox/<run_id>/staging/<package_slug>/`
2. Validate extracted tree
3. Read manifest
4. Build operation list
5. Dry-run operation list
6. Apply operation list
7. Capture results

## Dry Run
Before writing anything:
- resolve all destinations
- detect collisions
- detect illegal paths
- verify required sources exist
- verify parent directories can be created

## Collision Policy
Collision is blocking if:
- two packages in same run write same destination and no explicit order/overwrite rule exists
- package writes over file introduced earlier in same run without explicit allowance

## Rollback
Minimum viable rollback:
- backup touched files before apply
- on failure, restore backups for current package
- mark package failed
- do not archive as processed

## File Operation Report
Each applied target should record:
- source
- destination
- action
- result
- bytes_written
- duration_ms
- checksum_before
- checksum_after
