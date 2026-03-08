# Conflict Resolution

Duplicate sequence:
- mark both as conflict
- do not auto-apply
- emit failure report

Hash drift:
- treat it as a new artifact event
- record the new hash
- require revalidation

Missing sequence:
- block the plan or mark the plan partial, based on manifest policy

Foreign project slug:
- quarantine the ZIP
- record an orphan or foreign artifact finding
