# Test Plan

## Goal
Verify the ZIP intake pipeline is deterministic, safe and complete.

## Core Happy Path Tests
1. Two valid ZIPs in sequence install successfully
2. Registry reflects final processed state
3. Reports are generated
4. ZIPs are archived

## Validation Tests
1. Invalid filename -> quarantine
2. Duplicate sequence -> fail
3. Sequence gap -> fail
4. Project slug mismatch -> quarantine
5. Missing manifest -> quarantine
6. Manifest sequence mismatch -> quarantine

## Extraction and Path Safety Tests
1. ZIP with `../` path -> quarantine
2. ZIP with absolute path -> quarantine
3. Missing source target in manifest -> fail

## Wiring Tests
1. copy mode writes expected file
2. overwrite mode replaces existing file with backup
3. create_only fails when destination exists
4. fail_if_exists blocks overwrite
5. conflicting destinations between packages fail deterministically

## Test Runner Tests
1. required test fails -> run fails
2. optional test fails -> warning only
3. stdout/stderr captured to files

## Archive and Recovery Tests
1. processed ZIPs moved to archive
2. quarantined ZIPs moved to quarantine
3. failed apply rolls back current package
4. lock prevents concurrent second run

## Determinism Tests
1. same input -> same install plan
2. same input -> same registry ordering
3. same input -> same summary structure

## Recommended Test Structure
- unit tests for validators and schema
- integration tests for extraction/wiring
- end-to-end smoke test for full cycle
