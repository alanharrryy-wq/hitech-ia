# 04 Numbering and Naming Contract

## Numbering rule
Visible folders and human-facing files should start with two-digit prefixes:
- `00_`
- `01_`
- `02_`
- ...
- `99_`

## Why
Fast visual scanning, predictable sorting, low cognitive friction.

## Folder naming
Use short semantic names after the prefix.
Examples:
- `01_contracts`
- `02_modules`
- `03_prompts`
- `04_runs`

## File naming
Use the same prefix strategy inside folders.
Examples:
- `01_master_contract.md`
- `02_repo_layout_contract.md`
- `01_validate_repo_layout.py`

## Exceptions
Standard tool files may remain unprefixed when convention matters:
- `.gitignore`
- `.gitattributes`
- `LICENSE`
- `README.md` only if required by the platform

## Version suffixes
When keeping multiple generations, append a stable suffix:
- `01_core_v1.zip`
- `02_core_v2.zip`

## Slug style
Use lowercase with underscores for repo-managed files.
Avoid spaces.
