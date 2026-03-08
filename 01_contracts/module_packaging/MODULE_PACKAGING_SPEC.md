# Module Packaging Specification

## Purpose
The Module Packaging Engine turns a normalized module workspace into a canonical ZIP package
and delivers it into the HITECH-IA inbox.

## Inputs
- module workspace directory
- normalized `manifest.json`
- repository root

## Outputs
- canonical ZIP file
- `package_report.json`

## Responsibilities
- validate workspace shape
- calculate final sequence
- enforce canonical ZIP naming
- assemble package contents deterministically
- write checksum metadata
- deliver ZIP into `_zip_inbox/<project_slug>/`

## Canonical ZIP name
`zip<sequence>_<project_slug>_<package_slug>.zip`

## Determinism Rules
- same workspace + same manifest + same repo state -> same ZIP name
- packaging inventory must be sorted lexicographically
- report shape must be stable
