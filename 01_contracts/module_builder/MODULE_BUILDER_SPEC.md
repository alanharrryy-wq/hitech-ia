# Module Builder Specification

## Purpose
The Module Builder takes a source folder and converts it into a canonical HITECH-IA module package.

## Inputs
- source folder
- repository root
- optional project hint
- optional package hint

## Outputs
- normalized workspace
- `manifest.json`
- `builder_report.json`
- canonical ZIP package delivered to `_zip_inbox/<project_slug>/`

## Pipeline
1. validate source folder
2. build temporary canonical workspace
3. scan workspace
4. infer project/package/targets
5. build or repair manifest
6. package workspace
7. write final report

## Determinism Rules
- same source folder + same repo state -> same package result
- workspace copy ordering must be stable
- report structure must be stable

## Non-goals
- no installation into product repo
- no runtime apply
- no archive/quarantine behavior
