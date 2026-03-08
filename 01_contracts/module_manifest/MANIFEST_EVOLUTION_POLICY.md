# Manifest Evolution Policy

## Current schema version
`1.0`

## Compatibility
The engine should prefer forward-safe normalization:
- preserve known optional fields when valid
- keep `depends_on` if present and list-shaped
- keep `notes` if string-like

## Validation stance
Fail closed on:
- invalid slugs
- invalid sequence
- invalid targets
- invalid tests
- unsafe paths

Warn but preserve on:
- extra unknown top-level fields
- empty optional metadata
