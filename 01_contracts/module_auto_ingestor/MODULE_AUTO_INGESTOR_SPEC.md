# Module Auto Ingestor Specification

## Purpose
The Module Auto Ingestor scans `_zip_inbox`, detects project inboxes with pending ZIP artifacts,
and invokes the existing deterministic installer pipeline for those projects.

## Inputs
- repository root
- optional project filter
- optional mode (`dry_run` or `apply`)
- optional continuous watch mode

## Outputs
- `ingest_report.json`
- console summary
- optional repeated polling loop in watch mode

## Responsibilities
- discover active project inboxes
- determine which projects have pending installable ZIPs
- invoke `run_full_cycle.py` only for eligible projects
- collect per-project execution results
- write stable report output

## Non-goals
- no direct ZIP mutation
- no manifest generation
- no packaging
- no replacement for `run_full_cycle.py`
