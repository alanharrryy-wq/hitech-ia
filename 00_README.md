# hitech-ia

Artifact forge and Codex operations repo for HITECH.

## Purpose
This repository stores installable ZIP modules, contracts, prompts, run reports, templates, and schemas used to bootstrap or extend other repositories such as `hitech-os`.

## Design axioms
1. Artifact-first, not runtime-first.
2. Contracts before prompts.
3. ZIP modules are installable units.
4. Codex acts as controlled assembler, not free-form author.
5. Determinism over convenience.
6. Numbered folders and files for fast visual scanning.
7. Human-readable docs plus machine-readable schemas.
8. Temporary unpacking must stay outside the committed tree.

## Root layout
- `00_README.md`
- `01_contracts/`
- `02_modules/`
- `03_prompts/`
- `04_runs/`
- `05_reports/`
- `06_scripts/`
- `07_templates/`
- `08_schemas/`
- `09_examples/`
- `99_legacy_archive/` (optional; only if migration needs archival)

## Primary workflow
1. Store or version installable ZIP artifacts under `02_modules/`.
2. Download future intake ZIPs directly into `02_modules/_zip_inbox/<project_slug>/` using `zip<sequence>_<project_slug>_<package_slug>.zip`.
3. Store implementation contracts and repo laws under `01_contracts/`.
4. Store reusable Codex prompts under `03_prompts/`.
5. Store historical execution outputs under `04_runs/` and `05_reports/`.
6. Validate structure and manifests with scripts under `06_scripts/`.

## Non-goals
- Product runtime code.
- Large binaries unrelated to artifact installation.
- Ad-hoc dumps with no manifest.
- Hidden, undocumented experimental state.

## Repo status contract
A change is healthy only if:
- numbering remains consistent,
- manifests validate,
- schemas remain in sync with examples,
- prompts are self-contained,
- temporary unpack folders are ignored,
- legacy cleanup is documented.
