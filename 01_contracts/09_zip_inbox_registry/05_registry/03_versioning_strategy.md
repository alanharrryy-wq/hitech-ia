# Versioning Strategy

Registry file should carry:
- schema version
- generator version
- generated timestamp

Each project manifest should carry:
- manifest version
- project slug
- routing revision
- acceptance revision

A ZIP package version is primarily inferred from:
- sequence
- filename
- content hash
