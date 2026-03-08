# Auto Apply Guardrails

## Safety Rules
The ingestor must:
- invoke the existing runtime pipeline only
- never install more than requested scope
- support `dry_run` mode
- record failures without hiding them
- continue to other projects when one project fails

## Recommended defaults
- `mode=dry_run` for first-time verification
- `watch_interval_sec=15` in watch mode
- `max_loops=1` for oneshot behavior

## Failure Behavior
A failed project should produce:
- return code
- stdout/stderr capture
- report entry
