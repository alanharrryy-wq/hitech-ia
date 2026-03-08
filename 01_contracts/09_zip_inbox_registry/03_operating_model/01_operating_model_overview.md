# Operating Model Overview

This operating model standardizes how incoming ZIP packages are handled.

## Principles

1. One project, one inbox folder.
2. ZIP names carry sequence and identity.
3. Ordering is numeric, not lexicographic.
4. Registry state is generated from source artifacts, not edited manually.
5. Install operations are planned before they are applied.
6. Contract assets and runtime assets are routed separately.
7. Processed ZIPs are archived, not deleted.
8. Reports and ledgers explain what happened after every apply cycle.

## Neutral roles

### Operator
Downloads ZIP packages to the correct inbox folder and triggers validation or installation.

### Planner
Builds the internal registry and generates an install plan.

### Installer
Stages ZIPs, extracts content, routes files to targets, performs wiring and tests.

### Auditor
Reviews registry, reports, integrity hashes, archive notes and acceptance results.
