# Manifest Specification

Each ZIP should include a manifest file at one of these preferred paths:
1. `manifest.json`
2. `.hitech/manifest.json`

Recommended canonical path: `manifest.json`

## Required Fields
```json
{
  "schema_version": "1.0",
  "project_slug": "ui_observability",
  "package_slug": "core",
  "sequence": 1,
  "package_version": "0.1.0",
  "kind": "module",
  "wiring_mode": "copy",
  "targets": [],
  "tests": []
}
```

## Field Definitions

### `schema_version`
Manifest schema version. Start with `"1.0"`.

### `project_slug`
Must match ZIP filename project slug and parent inbox folder.

### `package_slug`
Must match ZIP filename package slug.

### `sequence`
Must match ZIP filename sequence.

### `package_version`
Human-readable artifact version.

### `kind`
Enum:
- `module`
- `config`
- `assets`
- `tests`
- `docs`
- `mixed`

### `wiring_mode`
Enum:
- `copy`
- `merge`
- `patch`
- `scripted`

`patch` and `scripted` must be tightly controlled and disabled unless explicitly allowed by repository policy.

### `targets`
Array of file routing intents.

Example:
```json
[
  {
    "source": "src/components/Widget.tsx",
    "destination": "apps/web/src/components/Widget.tsx",
    "mode": "overwrite",
    "required": true
  }
]
```

### `tests`
Array of commands or test intents to run after apply.

Example:
```json
[
  {
    "name": "smoke-ui",
    "type": "command",
    "command": "pnpm test:smoke",
    "required": true
  }
]
```

## Optional Fields
- `description`
- `depends_on`
- `provides`
- `conflicts_with`
- `post_apply`
- `notes`
- `ownership`
- `compatibility`

## `depends_on`
Example:
```json
[
  {
    "package_slug": "core",
    "min_sequence": 1
  }
]
```

## Validation Rules
Manifest is invalid if:
- any required field missing
- sequence mismatch
- project slug mismatch
- package slug mismatch
- duplicate destinations inside same artifact
- destination escapes repo root
- unsupported wiring mode
- test command empty when test entry exists

## Canonical Rule
ZIP filename and manifest must agree 100%.
If not, quarantine the artifact.
