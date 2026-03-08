# Structure Inference Specification

## Purpose
The Structure Inference Engine consumes a deterministic scan report and infers:
- project_slug
- package_slug
- tentative sequence
- target routing suggestions
- dependency hints

## Inputs
- `scan_report.json`
- repository root path

## Outputs
- `inference_report.json`

## Determinism Rules
- same scan report + same repo state -> same inference report
- candidate ranking must be stable
- slug output must be lowercase underscore style

## Minimum report fields
- schema_version
- inferred_at
- scan_report_path
- probable_project_slug
- project_resolution
- probable_package_slug
- target_suggestions
- dependency_hints
- warnings

## Project resolution modes
- `existing_project`
- `new_project`
