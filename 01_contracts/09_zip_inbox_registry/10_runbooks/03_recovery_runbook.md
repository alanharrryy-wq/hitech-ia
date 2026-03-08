# Recovery Runbook

If an apply fails:
1. stop further apply attempts for that project
2. preserve staging output for inspection if policy allows
3. write a failure report
4. move the offending ZIPs to `_failed/` or quarantine
5. refresh the registry
6. inspect last good ledger and archive note
7. only re-run after the input artifact set is understood
