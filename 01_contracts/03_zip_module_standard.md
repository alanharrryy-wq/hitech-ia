# 03 ZIP Module Standard v1

## Purpose
Define the installable unit format used by `hitech-ia` for Codex-driven delivery.

## Canonical filename convention
Installable ZIP artifacts must follow:

`zip<sequence>_<project_slug>_<package_slug>.zip`

Examples:
- `zip1_ui_observability_core.zip`
- `zip2_ui_observability_rules_reporting.zip`
- `zip3_ui_observability_graph_history.zip`

## Canonical package shape
Each module ZIP should contain:

```text
package/
  01_files/
  02_manifest/
    MANIFEST.json
  03_wire_plan/
    WIRE_PLAN.md
  04_acceptance/
    ACCEPTANCE.md
  05_codex_prompt/
    CODEX_INSTALL_PROMPT.txt
```

## Meaning
- `01_files/` contains the exact files to place into the target repo.
- `02_manifest/MANIFEST.json` declares identity, version, target repo, paths, and checksums.
- `03_wire_plan/WIRE_PLAN.md` explains where files go and what Codex may adjust.
- `04_acceptance/ACCEPTANCE.md` defines done, tests, and smoke checks.
- `05_codex_prompt/CODEX_INSTALL_PROMPT.txt` is the self-contained prompt Codex uses.

## Rules
1. ZIP payloads must be additive-first whenever possible.
2. If deletions are required, the manifest must declare them explicitly.
3. The package must be self-contained and readable offline.
4. File lists in manifest must be stable-sorted.
5. Checksums should be sha256 when practical.
6. Prompts must not require follow-up questions.
7. Install instructions must identify exact target paths.
8. Acceptance docs must prefer smoke tests before heavy suites.

## Recommended module partitioning
- `zip1_<project_slug>_core.zip`: reusable base implementation
- `zip2_<project_slug>_integration.zip`: target-specific wiring
- `zip3_<project_slug>_tests.zip`: validation and smoke additions
- `zip4_<project_slug>_docs.zip`: optional reference-only payload
