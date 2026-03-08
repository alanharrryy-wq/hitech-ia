from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_manifest_contract import validate_manifest_contract

class ValidateManifestContractTests(unittest.TestCase):
    def test_invalid_target_destination_is_rejected(self) -> None:
        manifest = {
            "schema_version": "1.0",
            "project_slug": "demo_project",
            "package_slug": "demo_pkg",
            "sequence": 1,
            "package_version": "0.1.0",
            "kind": "module",
            "wiring_mode": "copy",
            "targets": [{"source": "src/app.py", "destination": "../evil.py", "mode": "overwrite", "required": True}],
            "tests": [],
        }
        errors = validate_manifest_contract(manifest)
        self.assertTrue(errors)

    def test_valid_manifest_passes(self) -> None:
        manifest = {
            "schema_version": "1.0",
            "project_slug": "demo_project",
            "package_slug": "demo_pkg",
            "sequence": 1,
            "package_version": "0.1.0",
            "kind": "module",
            "wiring_mode": "copy",
            "targets": [{"source": "src/app.py", "destination": "src/app.py", "mode": "overwrite", "required": True}],
            "tests": [{"name": "smoke", "type": "command", "args": ["python", "-m", "unittest"], "required": True, "timeout_sec": 120, "env": {}}],
        }
        errors = validate_manifest_contract(manifest)
        self.assertFalse(errors)
