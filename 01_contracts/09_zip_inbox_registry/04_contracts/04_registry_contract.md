# Registry Contract

The internal registry is the generated system inventory for all inbox packages and their states.

Each registry entry must track:
- project slug
- sequence
- package slug
- original filename
- sha256
- file size
- last seen time
- lifecycle status
- archive path if processed
- validation findings

Registry states:
- `pending`
- `validated`
- `planned`
- `applied`
- `processed`
- `failed`
- `quarantined`

The registry should be machine-generated or machine-updated.
