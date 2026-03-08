# Acceptance Criteria

UniCodex work is complete only when all criteria below are true.

## Functional Completion
- ZIP naming validation exists
- sequence gap and duplicate detection exists
- manifest parsing exists
- extraction to staging exists
- routing/wiring exists
- backup and rollback exists
- tests run from manifest or plan
- report writing exists
- archive and quarantine flows exist
- lock exists

## Safety Completion
- no path traversal possible
- no writes outside repo allowlist
- concurrent runs blocked
- failures leave evidence
- strict failure statuses written

## Developer Experience
- one command runs full cycle
- report paths are obvious
- error messages are actionable
- examples exist
- tests exist

## Determinism
- same inputs yield stable ordering and stable report fields
- archive paths follow one fixed policy

## Done Definition
The system can take a clean project inbox with valid ZIPs and finish:
validate -> extract -> wiring -> tests -> report -> archive
without manual intervention.
