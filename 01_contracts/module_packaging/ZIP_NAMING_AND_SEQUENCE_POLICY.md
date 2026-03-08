# ZIP Naming And Sequence Policy

## Naming Rule
Every package must be named:

`zip<sequence>_<project_slug>_<package_slug>.zip`

## Sequence Allocation
- existing project -> max existing sequence + 1
- new project -> 1

## Collision Handling
If target ZIP path already exists:
- compare checksum
- if checksum matches, treat as deduplicated
- if checksum differs, fail closed

## Project Inbox Location
`02_modules/_zip_inbox/<project_slug>/`
