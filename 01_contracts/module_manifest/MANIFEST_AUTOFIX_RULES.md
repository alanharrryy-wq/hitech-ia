# Manifest Autofix Rules

## Safe Autofixes
The engine may safely:
- insert missing required fields from inference report
- normalize slug casing to lowercase underscore style
- normalize `tests` entries from legacy `command` strings into structured policy
- normalize `targets` arrays into deterministic ordering
- default `required=true` when omitted
- default `mode=overwrite` when omitted
- default `wiring_mode=copy` when omitted

## Unsafe Changes
The engine must NOT silently:
- change project/package slug to something unrelated to inference
- invent destinations outside deterministic rules
- allow path traversal
- permit unsupported wiring modes
- keep malformed `tests` entries without correction or warning
