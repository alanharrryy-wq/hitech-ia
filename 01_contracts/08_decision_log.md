# 08 Decision Log

## 2026-03-07
### Decision
Repurpose the old frontend-oriented repo into `hitech-ia`, an artifact forge and Codex operations repository.

### Why
- keep `hitech-os` lean,
- move ZIP bundles and prompt packs out of product repos,
- centralize reusable contracts and module artifacts,
- reduce friction for Codex installation workflows.

### Consequences
- old frontend runtime content may be removed or archived,
- the repo becomes documentation-and-artifact-heavy by design,
- numbering and deterministic naming become first-class UX.

## 2026-03-07
### Decision
Install a neutral ZIP inbox plus internal registry control plane centered on `02_modules/_zip_inbox/`.

### Why
- standardize intake with `zip<sequence>_<project_slug>_<package_slug>.zip`,
- guarantee project isolation and numeric ordering,
- produce deterministic registry/plan/report outputs for Codex/Unicodex workflows,
- support processed and failure archive handling without ad hoc steps.

### Consequences
- `06_scripts/04_zip_inbox_registry/` becomes the runtime entrypoint for inbox operations,
- schemas/examples/templates for the subsystem are now versioned under numbered roots,
- future ZIP deliveries can be processed end-to-end with a single full-cycle command.
