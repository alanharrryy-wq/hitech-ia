# OPPORTUNITY_MAP

## Scope
- Evidence-based opportunities only (no runtime edits applied in this task).

## Opportunities

### 1) Declare A Single Canonical Runtime Entry Path
- Evidence:
- `index.html` boots `/src/main.tsx`
- Parallel app compositions exist in `src/App.tsx`, `src/routes/Router.tsx`, `src/ui/App.tsx`, and `src/main.tsx.bak`
- Value:
- Reduces confusion during feature work and lowers accidental regression risk.

### 2) Resolve Static Asset Path Inconsistency
- Evidence:
- `index.html` references `/nf/ares_glow.css`
- Repository has `public/ares-glow.css`
- `public/nf/ares_glow.css` is absent
- Value:
- Avoids missing stylesheet behavior and visual drift.

### 3) Add Missing Operator README
- Evidence:
- `README.md` is missing
- Important behavior is currently spread across `DEPLOY_NOTES.md` and UI hints
- Value:
- Faster onboarding and fewer run/deploy assumptions.

### 4) Align Route Registration For `/`
- Evidence:
- `src/main.tsx` defines `/` -> `Home`
- `src/routes/register.ts` pushes `/` -> `Landing`
- Value:
- Eliminates ambiguous routing intent and clarifies default landing behavior.

### 5) Document Local Run Prerequisites
- Evidence:
- UI strings reference `RUN_Local.ps1`
- `RUN_Local.ps1` file is not present in this repo
- Value:
- Prevents operator dead-ends during local use.

### 6) Separate Demo Randomness From Health Logic
- Evidence:
- `src/pages/ModulesDashboard.tsx` uses random event generation (`Math.random`) and time-based IDs (`Date.now`)
- Value:
- Clearer monitoring semantics and easier deterministic testing.

## Priority Suggestion
- First: opportunities 1, 2, and 4 (highest confusion and runtime-behavior risk).
- Next: opportunities 3 and 5 (operator workflow clarity).
- Later: opportunity 6 (quality-of-life and testability).
