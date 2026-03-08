# Archive and Recovery Contract

Successfully consumed ZIPs move to `_processed/` with their original filenames preserved.

Failed ZIPs may:
- remain pending with a failure report
- move to `_failed/`
- be quarantined

Recovery operations must read:
- registry
- last plan
- last report
- ledger
- archive note

Rollback must be guided by the install report and only touch files introduced by the failed apply cycle.
