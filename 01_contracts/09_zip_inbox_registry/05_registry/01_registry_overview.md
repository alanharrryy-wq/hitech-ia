# Registry Overview

The internal registry is the central inventory of inbox packages.

It answers:
- what packages exist for one project
- whether order is complete
- whether hashes changed
- what has already been processed
- what failed last time
- where archives live

A registry contains:
- metadata about the registry file itself
- one object per project
- one entry per ZIP package
- validation summary
- lifecycle state
- ledger pointers
