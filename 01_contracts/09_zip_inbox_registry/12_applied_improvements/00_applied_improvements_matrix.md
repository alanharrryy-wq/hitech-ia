# Applied Improvements Matrix

This pack already materializes the following 30 functional improvements through concrete docs, schemas, templates, scripts and runbooks.

| # | Improvement | Materialized in |
|---|---|---|
| 1 | Canonical `zip<sequence>_` filename prefix | `04_contracts/02_naming_and_ordering_contract.md`, `07_examples/08_naming_examples.md` |
| 2 | Numeric ordering without zero padding | naming contract, validator script |
| 3 | One-project-per-folder isolation | `04_contracts/03_project_isolation_contract.md`, validator script |
| 4 | Foreign ZIP detection | validator script, conflict doc |
| 5 | Duplicate sequence detection | validator script, conflict doc |
| 6 | Sequence gap detection | validator script |
| 7 | Immutable source ZIP policy | inbox contract |
| 8 | Staging-before-apply rule | inbox contract, pipeline contract |
| 9 | Internal registry model | registry docs, schemas |
| 10 | SHA256 provenance tracking | registry contract, build registry script |
| 11 | Project manifest contract | manifest contract, manifest schema/template |
| 12 | Cross-repo routing model | routing contract, target map schema/example |
| 13 | Deterministic install plan generation | install pipeline contract, plan script |
| 14 | Dry-run first behavior | install request schema/template, Codex prompt template |
| 15 | Idempotency policy | pipeline contract |
| 16 | Processed archive flow | archive contract, mark processed script |
| 17 | Failed/quarantine flow | archive contract, archive policy script |
| 18 | Lock policy | manifest template, security contract |
| 19 | Report schema | `06_schemas/06_install_report.schema.json`, example |
| 20 | Ledger/report deliverables | Codex runbook, quality gates |
| 21 | Operator intake checklist | `08_templates/06_operator_intake_checklist.template.md` |
| 22 | Conflict resolution rules | registry conflict doc |
| 23 | Lifecycle states | `05_registry/02_lifecycle_states.md` |
| 24 | Versioning strategy | `05_registry/03_versioning_strategy.md` |
| 25 | Daily ops runbook | `10_runbooks/04_daily_ops_runbook.md` |
| 26 | Recovery runbook | `10_runbooks/03_recovery_runbook.md` |
| 27 | Neutral Codex install prompt | `08_templates/05_codex_install_prompt.template.txt` |
| 28 | Acceptance matrix | `11_acceptance/01_acceptance_matrix.md` |
| 29 | Non-regression rules | `11_acceptance/02_non_regression_rules.md` |
| 30 | Change control + quality gates | `11_acceptance/03_change_control.md`, `11_acceptance/04_quality_gates.md` |

The system described here is not just a plan. It is an operational reference pack with:
- defined rules
- defined schemas
- defined examples
- defined templates
- reference automation
- defined runbooks
- defined acceptance criteria
