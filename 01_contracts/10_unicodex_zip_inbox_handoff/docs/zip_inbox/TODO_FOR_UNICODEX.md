# TODO For UniCodex

## Priority 1
- Implement real lock in `run_full_cycle`
- Implement extraction path safety guard
- Implement manifest schema validator
- Implement routing engine from `targets`
- Implement required-test execution and capture
- Implement rollback for current package
- Implement archive/quarantine finalization

## Priority 2
- Add registry history snapshots
- Add checksum verification after archive move
- Add collision detection across same-run package targets
- Add summary markdown generator

## Priority 3
- Add dependency graph from `depends_on`
- Add richer merge semantics
- Add package compatibility checks
- Add optional install dry-run mode

## Non-Negotiable Rules
- do not guess destination rules
- fail closed on unsafe packages
- keep outputs deterministic
- keep feature flags OFF by default
