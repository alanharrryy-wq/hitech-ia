# Acceptance Matrix

A project intake flow is acceptable only if all of the following are true:

- every ZIP is inside a project folder
- every ZIP matches `zip<sequence>_<project_slug>_<package_slug>.zip`
- every ZIP project slug matches the folder name
- no duplicate sequences exist unless explicitly allowed by policy
- quality gates pass
- registry refresh succeeds
- install plan is deterministic
- report is written
- ledger is written
- processed ZIPs are archived or failed ZIPs are quarantined
