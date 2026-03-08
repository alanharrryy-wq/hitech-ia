# Neutral ZIP Inbox Registry Runtime Pack

This pack provides the executable reference layer for a neutral ZIP inbox installation system.

It is designed to be used together with the documentation pack:
- neutral_zip_inbox_registry_reference_pack.zip

## Purpose

This pack standardizes how a repository can:
- receive ZIP packages in a single inbox,
- classify them by project slug,
- order them by numbered sequence,
- validate metadata,
- build an internal registry,
- generate a deterministic install plan,
- archive processed ZIPs,
- produce machine-readable reports for an external automation or coding agent.

## Naming standard

Every ZIP must follow this format:

zip<sequence>_<project_slug>_<package_slug>.zip

Examples:
- zip1_ui_runtime_core.zip
- zip2_ui_runtime_rules.zip
- zip3_ui_runtime_graph_history.zip

## Neutral operating model

- The inbox repository stores incoming ZIP packages and reference metadata.
- A separate runtime repository may receive executable code, wiring, and integration artifacts.
- This pack does not hardcode any current project names.
- All generated outputs are deterministic and JSON-first.

## Suggested execution order

1. Validate inbox contents
2. Build registry snapshot
3. Generate install plan for a project slug
4. Execute unzip and installation steps in the target environment
5. Archive processed ZIPs
6. Rebuild registry snapshot

## Main scripts

- `06_scripts/04_zip_inbox_registry/validate_inbox.py`
- `06_scripts/04_zip_inbox_registry/build_registry.py`
- `06_scripts/04_zip_inbox_registry/make_install_plan.py`
- `06_scripts/04_zip_inbox_registry/archive_processed.py`
- `06_scripts/04_zip_inbox_registry/apply_archive_policy.py`
- `06_scripts/04_zip_inbox_registry/run_full_cycle.py`

## Intended usage with an external coding agent

Attach both ZIP packs to the same prompt:
1. reference pack
2. runtime pack

Then instruct the agent to:
- unpack both packs,
- install the docs into the neutral reference repository,
- install the scripts into the repository automation area,
- scan the ZIP inbox,
- build the registry,
- create the install plan,
- process the selected project slug.
