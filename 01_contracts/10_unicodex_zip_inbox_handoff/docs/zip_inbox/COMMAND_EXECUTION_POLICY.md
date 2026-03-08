# Command Execution Policy

## Goal
Execute manifest-defined tests deterministically without letting ZIP-provided commands escape through shell interpretation.

## Allowed test shape
Tests continue to use `"type": "command"`.

A test may now be declared in either of these forms:

### Legacy-compatible form
```json
{
  "name": "smoke-ui",
  "type": "command",
  "command": "python -m unittest -q",
  "required": true
}
```

### Preferred structured form
```json
{
  "name": "smoke-ui",
  "type": "command",
  "args": ["python", "-m", "unittest", "-q"],
  "cwd": ".",
  "timeout_sec": 300,
  "env": {
    "ZIP_SMOKE": "1"
  },
  "required": true
}
```

## Runtime rules
- `args` is preferred over `command`.
- If only `command` exists, runtime splits it into arguments and still executes with `shell=False`.
- `cwd` must be a safe relative path inside repo root.
- `timeout_sec` must be an integer between 1 and 3600.
- `env` must be a flat object of string keys and string values.
- Unsupported test types remain blocked.

## Security rules
- no `shell=True`
- no absolute `cwd`
- no path traversal in `cwd`
- no non-string env values
- fail closed on malformed command spec

## Operational note
This policy is intentionally minimal.
It improves the risk profile without expanding the ZIP inbox contract into a general-purpose task runner.
