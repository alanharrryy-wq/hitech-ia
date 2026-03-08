# System Map

## Flow

`ZIP downloads -> project inbox folder -> validation -> registry refresh -> install plan -> routing -> wiring -> tests -> archive -> report`

## Canonical project tree

```text
<contract-repo>/
  02_modules/
    _zip_inbox/
      <project_slug>/
        zip1_<project_slug>_<package_slug>.zip
        zip2_<project_slug>_<package_slug>.zip
        zip3_<project_slug>_<package_slug>.zip
```

## High-level routing model

### Contract repo receives
- inbox ZIP source packages
- project manifests
- contracts
- schemas
- examples
- prompts
- templates
- install reports
- registry files
- ledgers

### Runtime repo receives
- executable tool source
- CLI code
- analyzers
- providers
- adapters
- tests

## Internal registry

The internal registry is the source of truth for:
- what ZIPs exist
- which project they belong to
- sequence order
- integrity hashes
- install status
- last plan generated
- last apply attempt
- archive location

## Key design rule

ZIP packages remain immutable input artifacts. Routing, extraction, staging, apply operations and reports must be tracked separately.
