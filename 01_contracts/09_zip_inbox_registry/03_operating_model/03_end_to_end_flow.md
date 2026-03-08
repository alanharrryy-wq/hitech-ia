# End-to-End Flow

## Intake

The operator downloads ZIP packages directly to the project folder in the inbox. No manual renaming, reordering or relocation is required after download.

## Validation

The system validates:
- filename pattern
- project folder isolation
- duplicate sequences
- gaps in sequence
- forbidden files
- optional manifest presence

## Registry refresh

The system scans all ZIPs and creates or updates a registry file with:
- project slug
- sequence
- package slug
- sha256
- file size
- timestamps
- lifecycle status
- archive location
- last validation result

## Plan generation

A plan is generated for one project:
- apply order
- stage path
- route destinations
- preflight checks
- quality gates
- rollback boundaries

## Apply

The installer:
- creates a lock
- extracts ZIPs to staging
- validates staged content
- routes contract assets to the contract repo
- routes runtime assets to the runtime repo
- performs wiring
- runs tests
- writes report and ledger

## Closure

If the apply succeeds:
- ZIPs are moved to `_processed/`
- registry state becomes `processed`

If it fails:
- ZIPs move to `_failed/` or remain pending with a failure report
- no silent partial state is allowed
