# Scan Output Contract

## Output file
`scan_report.json`

## `input_type`
Allowed values:
- `zip`
- `directory`

## `kind`
Allowed values:
- `file`
- `directory`
- `archive_member`

## `signals`
Expected fields:
- `language_counts`
- `top_level_dirs`
- `noise_count`
- `suspicious_count`
- `probable_primary_language`
- `has_tests`
- `has_docs`
- `has_src`
- `has_manifest_candidate`

## Stability requirement
The scanner must preserve report shape even when warnings are present.
