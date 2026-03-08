# HITECH-IA ZIP Inbox Completion Pack

This pack is a **documentation handoff bundle** for UniCodex to finish the ZIP intake pipeline end to end:
validate -> registry -> plan -> extract -> wiring -> test -> report -> archive/quarantine.

## Goal
Turn the current ZIP inbox architecture into a deterministic installer for modular project artifacts.

## Scope
Assumed existing core scripts in repository:
- `validate_inbox.py`
- `build_registry.py`
- `make_install_plan.py`
- `run_full_cycle.py`
- archive/report helpers

Assumed intake root:
- `02_modules/_zip_inbox/<project_slug>/`

Assumed ZIP naming contract:
- `zip<sequence>_<project_slug>_<package_slug>.zip`

## What UniCodex should do
1. Read all docs in `docs/zip_inbox/`.
2. Implement any missing schemas, validators, extractors, routers, test runners and report writers.
3. Add safe locking, quarantine handling and archive determinism.
4. Make the full cycle runnable from one command.
5. Produce tests covering happy path and failure path.
6. Keep behavior deterministic and feature flags OFF by default.

## Deliverable expectation for UniCodex
- Working extraction and wiring
- Manifest-based routing
- Tests for sequence gaps, duplicates, bad manifests, routing failures, test failures
- Structured JSON reports
- Registry updates for all lifecycle transitions
- Quarantine for invalid or unsafe packages

## Pack contents
- `docs/zip_inbox/CONTRACT.md`
- `docs/zip_inbox/MANIFEST_SPEC.md`
- `docs/zip_inbox/WIRING_SPEC.md`
- `docs/zip_inbox/REGISTRY_SCHEMA.md`
- `docs/zip_inbox/REPORT_SCHEMA.md`
- `docs/zip_inbox/ARCHIVE_POLICY.md`
- `docs/zip_inbox/FAILURE_RECOVERY.md`
- `docs/zip_inbox/RUNBOOK.md`
- `docs/zip_inbox/TEST_PLAN.md`
- `docs/zip_inbox/ACCEPTANCE_CRITERIA.md`
- `docs/zip_inbox/TODO_FOR_UNICODEX.md`
- examples under `examples/`

## Important implementation note
This pack is intentionally **documentation-first**. It is meant to remove ambiguity so UniCodex can build the missing automation without asking follow-up questions.
