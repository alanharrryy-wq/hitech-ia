# 05 Codex Operating Contract

## Codex role
Codex is an installer, assembler, validator, and light conflict resolver.
Codex is not expected to invent architecture when a contract pack exists.

## Required behavior
1. Read the bundle docs before moving files.
2. Unpack into a temporary folder outside the target repo when possible.
3. Move `01_files/` payload into the declared repo paths.
4. Create missing folders only as specified.
5. Resolve small import or path mismatches only when necessary.
6. Prefer minimal, explicit changes.
7. Run smoke validation first.
8. Write a final report with created, modified, and deleted files.

## Conflict priority
1. Current repo reality
2. Contract pack docs and schemas
3. Prompt instructions

## Legacy cleanup policy
- Delete obvious starter files only when clearly unrelated to the new repo purpose.
- Archive uncertain leftovers under `99_legacy_archive/` with an archive note.
- Never silently drop files without reporting them.

## Output contract
The final report must include:
- summary,
- files created,
- files modified,
- files deleted,
- commands run,
- validation results,
- risks,
- next steps.
