# IMPACT_MAP

## Purpose
- Best-effort impact map for change planning in a small repository.
- Based only on observed imports, scripts, and static references.

## High-Impact Change Zones

### 1) Routing And Navigation
- Primary files:
- `src/main.tsx`
- `src/routes/register.ts`
- `src/components/NavBar.tsx`
- Direct effects:
- Path resolution for `/`, `/modules`, `/ares`, `/olimpo5`, `*`
- Navigation links shown in top bar
- Risk notes:
- Duplicate `/` route exists (`Home` and `Landing` through `extraRoutes`) -> behavior conflict risk (HYPOTHESIS; not executed)

### 2) Module Registry Contract
- Primary files:
- `public/modules.config.json`
- `src/modules.registry.ts`
- `src/pages/Landing.tsx`
- `src/pages/ModulesDashboard.tsx`
- `src/pages/WebModulePage.tsx`
- Direct effects:
- Which modules appear
- Which routes and URLs open
- Health/status behavior and mock flags
- Risk notes:
- Schema drift in `modules.config.json` can break list rendering or status checks

### 3) Desktop Bridge Integration
- Primary files:
- `src/hitechBridge.ts`
- `src/main.tsx`
- `src/components/OlympusCard.tsx`
- `index.html`
- Direct effects:
- Qt desktop signal wiring and command send flow
- Startup ping behavior
- Risk notes:
- `sendToDesktop("cmd:1:ping")` runs at module import time in `src/components/OlympusCard.tsx`

### 4) Static Asset And Overlay Layer
- Primary files:
- `index.html`
- `public/ui-theme.css`
- `public/overlay-controls.js`
- `public/quick-inject.js`
- `public/nf/modules_dashboard_v2.js`
- `public/nf/olympus_tech.js`
- `src/styles/overlay-fix.css`
- Direct effects:
- Global styling, floating controls, overlay stacking, runtime script side effects
- Risk notes:
- Asset path mismatch risk: `index.html` references `/nf/ares_glow.css` while file present is `public/ares-glow.css`

### 5) Build/Deploy Pipeline
- Primary files:
- `package.json`
- `vite.config.ts`
- `.github/workflows/pages.yml`
- `Dockerfile`
- Direct effects:
- Build base path behavior for GitHub Pages
- CI deployment path and runtime BASE_URL expectations

## Medium-Impact Zones
- `src/pages/ModulesDashboard.tsx` local event generator and status poller logic
- `src/pages/WebModulePage.tsx` embed/open fallback logic
- `src/modules.registry.ts` fetch and normalization behavior

## Low-Confidence Or Legacy Zones
- Files indicating alternate/older app path:
- `src/ui/App.tsx`
- `src/main.tsx.bak`
- `src/App.tsx`
- `src/routes/Router.tsx`
- `src/modules/*` background/settings/task set (mostly reachable from `src/ui/App.tsx`)
- Impact status:
- HYPOTHESIS: currently inactive in default runtime because `index.html` boots `/src/main.tsx`
