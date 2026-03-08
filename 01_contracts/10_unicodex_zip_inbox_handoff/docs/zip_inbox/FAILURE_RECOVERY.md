# Failure Recovery

## Failure Classes
1. Validation failure
2. Extraction failure
3. Manifest failure
4. Wiring failure
5. Test failure
6. Archive failure
7. Lock failure

## Recovery Principles
- fail closed
- preserve evidence
- write report even on failure
- avoid half-applied invisible state

## Minimum Evidence to Preserve
- failing ZIP path
- run_id
- package_slug
- error class
- stack trace or stderr
- touched destinations
- rollback result

## Rollback Levels

### Validation failure
No writes should occur.

### Extraction failure
Delete partial staging directory and quarantine ZIP if appropriate.

### Wiring failure
Restore backed-up files for current package.

### Test failure
Policy choice:
- strict mode: rollback package changes from current run
- permissive mode: keep apply but mark run failed
Recommended default: strict for required tests.

### Archive failure
Do not declare processed if move/archive finalization fails.

## Idempotency
Re-running after a failure should not corrupt the repo.
A failed package should be reprocessable after the issue is fixed.
