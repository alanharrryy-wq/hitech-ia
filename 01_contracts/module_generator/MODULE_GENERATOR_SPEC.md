# Module Generator Specification

## Purpose
The ZIP Module Generator turns a structured module spec into a source workspace and then
delegates packaging to the Module Builder.

## Inputs
- module spec JSON
- repository root
- optional output report path

## Outputs
- generated source workspace
- `generation_report.json`
- final canonical ZIP delivered through builder

## Pipeline
1. parse spec
2. generate module skeleton
3. generate docs
4. generate tests
5. seed manifest template
6. invoke builder
7. write final report
