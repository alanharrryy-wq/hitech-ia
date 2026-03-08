# Security and Integrity Contract

Every ZIP should be hashed using SHA256 during registry generation.

The installer trusts only:
- the file actually present in the inbox
- the hash recorded during planning
- the manifest active during planning
- the generated plan

Only one apply cycle per project may run at a time.

Forbidden shortcuts:
- applying without staging
- applying without a plan
- applying with mismatched hash
- deleting source ZIPs without archival record
