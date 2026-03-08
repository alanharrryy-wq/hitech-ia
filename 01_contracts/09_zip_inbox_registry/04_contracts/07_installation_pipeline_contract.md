# Installation Pipeline Contract

Stages:
1. discover inbox packages
2. validate names and project isolation
3. refresh registry
4. read manifest
5. generate plan
6. acquire lock
7. stage extraction
8. preflight validation
9. route files
10. apply wiring
11. run tests
12. write report and ledger
13. archive or quarantine packages
14. release lock

The same inbox content plus the same manifest must generate the same plan order.

An already processed ZIP with the same hash must not be applied again unless explicitly forced.
