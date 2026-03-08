# 06 Acceptance Contract

## Bootstrap definition of done
The `hitech-ia` repo is considered bootstrapped when:
1. Root numbered layout exists.
2. Core contracts are present.
3. Schemas exist and examples validate against them.
4. Prompt folder contains at least one installer prompt and one usage prompt.
5. Module shelves exist with README placeholders.
6. Run and report folders exist with README placeholders.
7. Validation script exits successfully.
8. Legacy handling is explicit: cleaned, archived, or absent.

## Required smoke checks
- Repo validator runs successfully.
- Manifest example validates against schema.
- ZIP package example validates against schema.
- Prompt request example validates against schema.

## Quality bar
- deterministic ordering,
- no ad-hoc roots,
- numbered docs present,
- no unresolved TODOs in required contracts,
- no temporary unpack artifacts committed.
