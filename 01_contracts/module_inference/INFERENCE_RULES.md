# Inference Rules

## Project Inference
Priority order:
1. explicit CLI project hint
2. exact match against existing inbox project folders
3. best token overlap against existing project folders
4. fallback to normalized source-derived slug

## Package Inference
Priority signals:
1. dominant top-level source directory name
2. source archive/file stem
3. fallback to primary language + role signal
4. final fallback: `module_core`

## Target Suggestions
Suggested target routing is conservative:
- `src/**` -> `src/**`
- `tests/**` or `test/**` -> `tests/**`
- `docs/**` and `*.md` -> `docs/**`
- configuration files -> `config/**`
- everything else text-like -> `assets/**`

## Sequence Tentative
Sequence is tentative only and equals:
- max existing ZIP sequence + 1 for existing project
- 1 for new project
