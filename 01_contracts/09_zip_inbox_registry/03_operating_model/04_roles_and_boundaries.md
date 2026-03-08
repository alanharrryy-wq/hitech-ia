# Roles and Boundaries

## Operator boundary
The operator only needs to:
- download ZIP packages into the right project inbox folder
- trigger validation, planning or installation

The operator does not need to:
- manually reorder ZIPs
- manually move files into final targets
- manually maintain the registry
- manually rename ZIPs after the naming standard is adopted

## Installer boundary
The installer is responsible for:
- respecting numeric sequence order
- reading the project manifest
- routing content to the correct repo targets
- writing reports and ledgers
- enforcing quality gates

## Registry boundary
The registry must not be used as a hand-edited planning scratchpad. It is derived state and should be regenerated from the inbox plus manifests.

## Archive boundary
Processed ZIPs remain part of provenance history. They are archived, not destroyed.
