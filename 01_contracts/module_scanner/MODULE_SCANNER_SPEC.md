# Module Scanner Specification

## Purpose
The Module Scanner inspects a raw ZIP artifact or a source folder and emits a deterministic scan report.

## Goals
- Produce a stable inventory of files
- Identify likely languages and project characteristics
- Flag junk, noise, and suspicious content
- Serve as the first stage for later inference, manifest, and packaging steps

## Inputs
- ZIP file path
- or source directory path

## Outputs
- `scan_report.json`

## Determinism Rules
- File ordering must be lexicographic and case-insensitive
- Identical input must produce identical inventory ordering
- Summary counts must be derived from ordered inventory only

## Minimum report fields
- schema_version
- scanned_at
- input_path
- input_type
- inventory
- summary
- signals
- warnings

## Inventory item fields
- relative_path
- extension
- size_bytes
- kind
- top_level_dir
- language_guess
- is_noise
- is_suspicious

## Noise examples
- `__pycache__/`
- `.pytest_cache/`
- `.DS_Store`
- `Thumbs.db`
- `node_modules/`
- `dist/`
- `build/`

## Suspicious examples
- executable binaries
- DLL/SO/DYLIB artifacts
- archive-inside-archive
- private keys
- path traversal inside ZIP members

## CLI
```bash
python 06_scripts/module_scanner/scan_module.py --input <zip_or_folder> --output <report.json>
```
