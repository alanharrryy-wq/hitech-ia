# Module Layout Standard

## Canonical workspace layout
The builder creates or preserves a module workspace with these top-level conventions when present:

- `src/`
- `tests/`
- `docs/`
- `config/`
- `manifest.json`

## Allowed source shapes
The source folder may already be:
- canonical
- semi-structured
- flat

The builder should preserve useful content while normalizing layout.

## Preservation Rules
- preserve relative paths for text assets
- do not invent source code
- copy docs and tests when present
- ignore common noise directories and files
