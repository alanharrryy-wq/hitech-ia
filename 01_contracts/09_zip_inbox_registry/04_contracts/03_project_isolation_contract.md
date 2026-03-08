# Project Isolation Contract

Every project gets exactly one inbox folder:

`<contract-repo>/02_modules/_zip_inbox/<project_slug>/`

For packages inside one project folder, the `<project_slug>` segment in every ZIP filename must match the folder name exactly.

Forbidden states:
- multiple project slugs mixed in one folder
- one ZIP placed directly in `_zip_inbox/`
- ZIPs with no project folder
- renamed project folders without updated manifest
