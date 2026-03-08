# Registry Schema

Registry is a structured snapshot of inbox artifacts and their lifecycle.

## Recommended file
`03_registry/zip_inbox/<project_slug>/registry.latest.json`

## Recommended history
`03_registry/zip_inbox/<project_slug>/history/registry.<timestamp>.json`

## Schema
```json
{
  "schema_version": "1.0",
  "project_slug": "ui_observability",
  "generated_at": "2026-03-07T12:00:00Z",
  "items": [
    {
      "sequence": 1,
      "zip_name": "zip1_ui_observability_core.zip",
      "package_slug": "core",
      "sha256": "abc123",
      "size_bytes": 12345,
      "status": "validated",
      "archive_path": null,
      "quarantine_path": null,
      "manifest_path": "manifest.json",
      "errors": [],
      "warnings": []
    }
  ]
}
```

## Item Fields
- `sequence`: integer
- `zip_name`: original filename
- `package_slug`: slug from filename
- `sha256`: ZIP checksum
- `size_bytes`: file size
- `status`: lifecycle state
- `archive_path`: final archived location if processed
- `quarantine_path`: final quarantine location if quarantined
- `manifest_path`: manifest path inside ZIP if found
- `errors`: validation/apply errors
- `warnings`: non-blocking notes

## Status Transition Rules
Allowed progression:
`pending -> validated -> planned -> applied -> processed`

Failure routes:
- `pending -> failed`
- `validated -> failed`
- `pending -> quarantined`
- `validated -> quarantined`
- `planned -> failed`
- `applied -> failed`

`processed` is terminal.
`quarantined` is terminal for that specific artifact.
