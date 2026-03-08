# Manifest Engine Specification

## Purpose
The Manifest Engine creates, repairs, and validates `manifest.json` for HITECH-IA module packages.

## Inputs
- `inference_report.json`
- optional existing `manifest.json`

## Outputs
- normalized `manifest.json`
- `manifest_report.json`
- optional unified diff of before/after

## Responsibilities
- build manifest from inference
- normalize target and test policy
- autofix safe structural problems
- validate required fields and path safety
- produce deterministic output

## Determinism Rules
- field ordering must be stable
- targets must be sorted by destination then source
- tests must be sorted by name then type
- same input should produce same manifest body

## Non-goals
- no packaging
- no repo mutation outside manifest/report files
- no sequence allocation beyond values already inferred
