# 07 Wiring and Install Contract

## Target repo assumption
This pack is intended for a repository being repurposed into `hitech-ia`.
The repo may previously have been a frontend application repository.

## Install flow
1. Read root docs from the package.
2. Stage unpacked files outside the repo or under a temporary ignored folder.
3. Copy `package/01_files/` into repo root, preserving relative paths.
4. Remove or archive legacy files according to the operating contract.
5. Run repo validator.
6. Update README if local repo naming differs.
7. Commit only after validation passes.

## Allowed light rewiring
- adjust path casing,
- fix minor markdown links,
- add archive notes,
- tune validator path constants.

## Forbidden rewiring
- changing folder meanings,
- introducing new root folders without contract updates,
- dropping schemas or prompts,
- adding runtime app code unrelated to repo purpose.
