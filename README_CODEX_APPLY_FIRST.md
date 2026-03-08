# HITECH-IA ZIP Inbox Hardening Delta Pack

This pack is **not** a completion pack.
It is a **surgical hardening delta** for the ZIP inbox runtime that already exists in the repository.

## Why this exists
The runtime in commit `0451d7e` already covers the main lifecycle:
validate -> registry -> plan -> extract -> wiring -> test -> report -> archive/quarantine.

The remaining high-value gap is **command execution hardening** for manifest-driven tests.
The current runtime still executes manifest test commands through a shell.
This delta removes that risk while keeping the manifest contract backwards-compatible.

## What Codex should do
1. Copy these files into the repository preserving paths exactly.
2. Prefer these files over existing same-path files. They are full-file replacements, not partial snippets.
3. Run:
   - `python -m py_compile run_full_cycle.py 06_scripts/04_zip_inbox_registry/*.py`
   - `python -m unittest discover -s 06_scripts/04_zip_inbox_registry/tests -v`
4. If minor import or path issues appear, fix only what is necessary.
5. Do not rename the pack files unless a repo naming conflict forces it.
6. Do not re-open the old completion scope. Keep the change focused on hardening.

## Files in this pack
- new: `06_scripts/04_zip_inbox_registry/command_policy.py`
- replace: `06_scripts/04_zip_inbox_registry/manifest_validator.py`
- replace: `06_scripts/04_zip_inbox_registry/test_executor.py`
- new: `06_scripts/04_zip_inbox_registry/tests/test_command_execution_hardening.py`
- replace: `09_examples/07_unicodex_zip_inbox_handoff/manifest.example.json`
- docs:
  - `01_contracts/10_unicodex_zip_inbox_handoff/docs/zip_inbox/COMMAND_EXECUTION_POLICY.md`
  - `01_contracts/10_unicodex_zip_inbox_handoff/docs/zip_inbox/HARDENING_DELTA.md`
  - `01_contracts/10_unicodex_zip_inbox_handoff/docs/zip_inbox/TODO_FOR_UNICODEX_HARDENING.md`

## Expected result
- Manifest tests can run without `shell=True`
- Existing string commands stay supported
- Structured `args` commands become first-class
- Test timeouts are deterministic
- Test `cwd` stays inside repo root
- Test environment overrides are explicit and bounded
- New hardening tests pass

## Important guardrail
This pack deliberately avoids changing batch semantics, dependency graph behavior, or broad registry contracts.
It only hardens the most exposed surface with minimal repo churn.
