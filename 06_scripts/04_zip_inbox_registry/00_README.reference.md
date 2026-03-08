# Scripts Reference

These scripts are dependency-light Python reference utilities for operating the ZIP inbox model.

- `01_validate_inbox_structure.py` : validates folder isolation, filename rules, duplicates and gaps
- `02_build_registry_from_inbox.py` : scans the inbox and emits a registry JSON
- `03_generate_install_plan.py` : creates a deterministic install plan for one project
- `04_mark_processed_zip.py` : archives successfully applied ZIPs into `_processed/`
- `05_apply_archive_policy.py` : moves failed ZIPs into `_failed/` or quarantine

These are reference implementations, intentionally neutral and designed to be adapted into a real toolchain.
