# REPO_MAP

## Scope
- Target repo: `hitech-ia`
- Source of truth: local filesystem scan (`docs/_generated/FILE_INDEX.json`) and local file reads only
- Runtime code status: untouched by this docs run

## Snapshot
- Git available: `true`
- Branch: `fix/desktop-bridge`
- HEAD: `26d78678ac9277e929377f0f26dea162f5523fce`
- Dirty worktree at scan time: `true`
- Pre-doc file count (filtered): `58`
- Top-level split (pre-doc): `.github=1`, `.vscode=1`, `(root)=11`, `public=10`, `src=35`

## Entrypoints
- HTML entry: `index.html`
- Vite runtime entry script in HTML: `/src/main.tsx`
- React bootstrap: `src/main.tsx`
- Router shell owner: `src/main.tsx`
- Optional legacy boot path file: `src/main.tsx.bak` (not referenced by `index.html`)

## Build And Deploy Tooling
- Package scripts from `package.json`:
- `dev`: `vite`
- `build`: `vite build`
- `preview`: `vite preview --host`
- Bundler config: `vite.config.ts`
- Env-driven base/deploy toggles:
- `PAGES_BASE` -> Vite `base`
- `PAGES_DEPLOY` -> `import.meta.env.PAGES_DEPLOY`
- CI deploy workflow: `.github/workflows/pages.yml`
- Docker dev runner: `Dockerfile`

## Runtime Topology
- Primary route tree is in `src/main.tsx`
- Declared routes:
- `/` -> `Home`
- `/modules` -> lazy `ModulesDashboard`
- extra routes from `src/routes/register.ts`
- `/olimpo5` -> `Olimpo5`
- `*` -> `NotFound`
- Extra route registrations in `src/routes/register.ts`:
- `/` -> `Landing`
- `/ares` -> `AresPanel`
- Module registry contract:
- Registry file: `public/modules.config.json`
- Loader: `src/modules.registry.ts`
- Consumers: `src/pages/Landing.tsx`, `src/pages/ModulesDashboard.tsx`, `src/pages/WebModulePage.tsx`
- Desktop bridge contract:
- Bridge code: `src/hitechBridge.ts`
- Bridge init and ping trigger: `src/main.tsx`
- QWebChannel-related assets: `index.html`, `public/qwebchannel.js`

## Notable Parallel Or Legacy Paths
- `src/App.tsx` + `src/routes/Router.tsx` define another router composition.
- `src/ui/App.tsx` defines another UI shell (background/settings/tasks stack).
- `src/main.tsx.bak` references `src/ui/App.tsx`.
- `src/styles.css.add` looks like a patch fragment.

## Classification
- This is **not** a skeleton repo.
- Evidence: it has active Vite scripts, concrete route wiring, deploy workflow, module registry, and desktop bridge logic.
- Best fit: **actual minimal app with layered legacy/kit artifacts** (some files indicate prior or alternate entry paths).

