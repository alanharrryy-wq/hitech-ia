# Internal Registry Model

The internal registry is the machine-generated map of all installable ZIP artifacts across all project inbox folders.

Minimum responsibilities:
- inventory all ZIP packages
- store parsed sequence, project and package slug
- store hash and size
- store lifecycle status
- keep last validation results
- remember archive location
- support plan generation
- support recovery decisions

Recommended registry files:
- `registry.generated.json`
- `registry.history.jsonl`
- `project/<project_slug>/latest_plan.json`
- `project/<project_slug>/latest_report.json`

The registry is the operational truth layer between inbox artifacts and final installation.
