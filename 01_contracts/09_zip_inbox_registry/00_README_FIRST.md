# Neutral ZIP Inbox + Internal Registry Reference Pack

This pack defines a neutral, reusable operating model for handling incoming development ZIP packages in a deterministic way.

## Core idea

A user downloads ZIP packages directly into a single inbox tree:

`<contract-repo>/02_modules/_zip_inbox/<project_slug>/`

From there, an installer or Codex worker can:

1. scan the inbox
2. validate ZIP names and order
3. build an internal registry
4. generate an installation plan
5. route files to the proper target repositories
6. archive processed ZIPs
7. write an install report

## Canonical filename format

`zip<sequence>_<project_slug>_<package_slug>.zip`

Examples:

- `zip1_ui_observability_core.zip`
- `zip2_ui_observability_rules_reporting.zip`
- `zip3_ui_observability_graph_history.zip`

The numeric prefix is parsed numerically, so `zip10` sorts after `zip9` even without zero padding.

## Repository roles

This pack is neutral. It uses the following generic roles:

- **contract repo**: stores contracts, manifests, schemas, templates, examples, prompts, inbox, registry and reports
- **runtime repo**: stores executable tooling, agents, CLIs, analyzers, integrations and tests

## What is included

- operating contracts
- registry model
- schemas
- examples
- templates
- reference scripts
- runbooks
- acceptance rules
- 30 applied functional improvements

## Recommended top-level inbox location

`<contract-repo>/02_modules/_zip_inbox/`

Each project gets its own folder:

`<contract-repo>/02_modules/_zip_inbox/<project_slug>/`

## Minimal operator workflow

1. Download ZIP packages directly into the right project folder inside `_zip_inbox`
2. Run inbox validation
3. Build or refresh the registry
4. Generate the install plan for one project
5. Execute routing, wiring and tests
6. Mark packages as processed and archive them
7. Keep the report and ledger

This pack avoids mixing unrelated projects and turns ZIP intake into a deterministic pipeline.
