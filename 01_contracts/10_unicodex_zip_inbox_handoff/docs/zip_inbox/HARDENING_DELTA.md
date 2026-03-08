# Hardening Delta

## Why a delta instead of another completion pack
The repository already contains the major ZIP inbox lifecycle implementation.
Re-sending the old completion pack would create duplicate intent and drift.

This delta focuses on the remaining sharp edge:
manifest-driven test execution.

## What changed
- new helper for command normalization and runtime policy
- manifest validator extended to normalize:
  - `args`
  - `cwd`
  - `timeout_sec`
  - `env`
- test executor now uses:
  - `shell=False`
  - deterministic timeout handling
  - repo-bound cwd resolution
  - explicit environment overlay
- new tests added for:
  - structured args
  - cwd traversal rejection
  - timeout failure path
  - environment override flow

## What intentionally did not change
- archive structure
- quarantine structure
- package sequencing
- registry top-level shape
- wiring semantics
- batch stop-on-first-failure behavior
- dependency graph semantics

## Success condition
After copying this delta into the repo, Codex should need only small fixes, then run compile + unittest and stop.
