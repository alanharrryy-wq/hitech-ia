# Inbox Polling Policy

## Discovery Root
`02_modules/_zip_inbox/`

## Eligible project definition
A project is eligible for ingestion if:
- its inbox folder exists
- it contains at least one `.zip`
- ZIP names are not only archived/quarantine artifacts
- the folder is not a reserved internal folder

## Polling modes
- `oneshot`: scan once and exit
- `watch`: poll every N seconds and process newly eligible projects

## Stability
Project ordering must be lexicographic and case-insensitive.
