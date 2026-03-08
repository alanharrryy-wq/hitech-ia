# Neutral Glossary

- **contract repo**: repository that stores contracts, inbox, schemas, examples, prompts, registry and reports
- **runtime repo**: repository that stores the executable tooling and tests
- **project slug**: neutral, lowercase identifier for one tool or module family
- **package slug**: neutral, lowercase identifier for one ZIP stage
- **sequence**: numeric install order extracted from `zip<sequence>_`
- **registry**: generated inventory of inbox packages and their lifecycle state
- **manifest**: project-level routing and install metadata
- **plan**: deterministic list of actions to apply one project
- **ledger**: append-only operational summary of what was applied
- **staging**: temporary extraction area ignored by version control
- **processed**: package successfully consumed and archived
- **failed**: package validated or applied unsuccessfully and requires review
- **orphan ZIP**: ZIP that does not match the canonical filename rule or project folder identity
