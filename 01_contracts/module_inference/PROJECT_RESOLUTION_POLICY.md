# Project Resolution Policy

## Source of truth
Project folders under:
`02_modules/_zip_inbox/<project_slug>/`

## Existing project match
A project is considered existing when:
- exact slug match exists, or
- overlap score exceeds safe threshold and is top ranked

## New project creation hint
If no safe existing project match exists:
- classify as `new_project`
- recommend `tentative_sequence = 1`

## Confidence
Provide confidence as:
- `high`
- `medium`
- `low`
