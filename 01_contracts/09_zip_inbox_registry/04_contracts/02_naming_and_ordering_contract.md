# Naming and Ordering Contract

## Canonical filename
`zip<sequence>_<project_slug>_<package_slug>.zip`

### Examples
- `zip1_data_pipeline_core.zip`
- `zip2_data_pipeline_rules_reporting.zip`
- `zip3_data_pipeline_graph_history.zip`

### Rules
- `sequence` is a positive integer and determines order
- `project_slug` is lowercase snake case
- `package_slug` is lowercase snake case
- ordering is numeric, not text-based

Invalid names include:
- missing `zip` prefix
- no numeric sequence
- spaces
- mixed case
- extra project slug changes inside a project folder
