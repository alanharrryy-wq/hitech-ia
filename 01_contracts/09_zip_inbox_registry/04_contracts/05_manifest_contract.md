# Project Manifest Contract

Each project folder may define a `project.manifest.json` file that tells the planner how to route and validate packages.

Minimal manifest fields:
- project slug
- contract repo path
- runtime repo path
- routing rules
- expected sequence policy
- test commands
- archive policy
- lock policy

Project manifest rules override generic defaults for that project only.
