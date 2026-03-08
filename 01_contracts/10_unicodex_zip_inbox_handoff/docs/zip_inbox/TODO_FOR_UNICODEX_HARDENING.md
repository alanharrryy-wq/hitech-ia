# TODO For UniCodex Hardening Delta

## Mandatory
- Copy all full-file replacements and new files from this pack into the repo
- Keep path names exactly as provided unless the repo forces a tiny import fix
- Run py_compile for root wrapper and runtime Python files
- Run unittest discovery for `06_scripts/04_zip_inbox_registry/tests`
- Fix only minimal breakage required for green tests

## Verify
- legacy string command tests still pass
- structured `args` tests pass
- timeout path reports a failed required test instead of crashing
- unsafe `cwd` is rejected during manifest validation
- no use of `shell=True` remains in test execution

## Do not expand scope
- do not redesign registry schemas
- do not change archive folders
- do not introduce third-party dependencies unless absolutely forced
- do not reopen the older completion-pack TODO list
