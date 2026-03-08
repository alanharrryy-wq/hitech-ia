# Codex C - Block 1 Docs Maps (hitech-ia)

## Objective
- Produce docs-only repository maps with runtime untouched.
- Outputs requested:
- `NOTEBOOK.md`
- `docs/REPO_MAP.md`
- `docs/IMPACT_MAP.md`
- `docs/OPPORTUNITY_MAP.md`
- `docs/_generated/FILE_INDEX.json`
- `docs/_generated/CHANGE_SAFELOG.md`

## Artifact Links
- `docs/REPO_MAP.md`
- `docs/IMPACT_MAP.md`
- `docs/OPPORTUNITY_MAP.md`
- `docs/_generated/FILE_INDEX.json`
- `docs/_generated/CHANGE_SAFELOG.md`

## Git Snapshot
- Git available: `true`
- Branch: `fix/desktop-bridge`
- HEAD: `26d78678ac9277e929377f0f26dea162f5523fce`
- Dirty: `true`
- Note: standard git calls initially showed safe-directory ownership protection; metadata was read with `git -c safe.directory=<repo>`

## Key Findings
- Build system is Vite + React + TypeScript.
- Runtime HTML entry is `index.html` -> `/src/main.tsx`.
- Deploy path is configured for GitHub Pages in `.github/workflows/pages.yml` with `PAGES_BASE=/hitech-ia/` and `PAGES_DEPLOY=true`.
- Module registry pattern is active (`public/modules.config.json` + `src/modules.registry.ts` + registry consumers).
- Desktop bridge wiring is present (`src/hitechBridge.ts`, `qwebchannel`, startup ping).

## ANOMALIES
- File-count expectation check:
- Prior expectation: around `57` files.
- Observed filtered pre-doc snapshot: `58` files (`docs/_generated/FILE_INDEX.json`).
- Directory existence check (required):
- `src/` exists: `true`
- `app/` exists: `false`
- Package scripts check (required):
- `dev`: `vite`
- `build`: `vite build`
- `preview`: `vite preview --host`
- Skeleton vs partial vs minimal-app check (required):
- Conclusion: **actual minimal app**, not a skeleton.
- Additional nuance: signs of layered/partial export history (parallel entry/legacy artifacts such as `src/main.tsx.bak`, `src/ui/App.tsx`, `src/App.tsx`).
- HYPOTHESIS:
- Duplicate `/` route intent conflict (`Home` in `src/main.tsx` and `Landing` pushed in `src/routes/register.ts`).
- HYPOTHESIS:
- Static CSS path mismatch risk: `index.html` references `/nf/ares_glow.css`, but observed file is `public/ares-glow.css`; `public/nf/ares_glow.css` is absent.
- Missing operator file:
- UI references `RUN_Local.ps1`, but file is absent in repo.
- Missing baseline docs:
- `README.md` absent.

## Determinism And Safety Notes
- Offline-only workflow; no installs and no network fetches executed.
- Deterministic file index ordering used (ordinal sorted paths).
- Runtime source files outside allowed docs scope were not edited by this task.

