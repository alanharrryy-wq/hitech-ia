# Cross-Repo Routing Contract

One project install may write to more than one repository.

### Contract repo destinations
- contracts
- schemas
- examples
- prompts
- templates
- reports
- ledgers

### Runtime repo destinations
- executable tool source
- CLI source
- analyzers
- providers
- integrations
- runtime tests

Routing must be derived from:
1. project manifest
2. plan rules
3. content selectors
4. quality gates

The installer must not dump extracted content into target repos without route validation.
