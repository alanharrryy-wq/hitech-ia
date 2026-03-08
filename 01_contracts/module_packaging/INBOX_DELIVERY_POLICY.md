# Inbox Delivery Policy

## Delivery Rules
- do not deliver outside `_zip_inbox`
- do not overwrite a different ZIP under same target path
- ensure project inbox folder exists
- emit report for every packaging attempt

## Workspace Expectations
Workspace should contain:
- `manifest.json`
- zero or more payload files or directories

## Non-goals
- no installation
- no archive/quarantine handling
- no inference
