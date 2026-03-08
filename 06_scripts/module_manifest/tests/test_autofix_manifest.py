from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from autofix_manifest import autofix_manifest

class AutofixManifestTests(unittest.TestCase):
    def test_legacy_command_is_normalized_to_args(self) -> None:
        inference = {
            "probable_project_slug": "api_core",
            "probable_package_slug": "auth_adapter",
            "project_resolution": {"tentative_sequence": 3},
            "target_suggestions": [{"source": "src/auth.py", "destination": "src/auth.py", "required": True}],
        }
        existing = {
            "project_slug": "API-CORE",
            "package_slug": "Auth Adapter",
            "sequence": "3",
            "tests": [{"name": "smoke", "type": "command", "command": "python -m unittest"}],
            "targets": [{"source": "src/auth.py", "destination": "src/auth.py"}],
        }
        manifest, metadata, warnings = autofix_manifest(existing, inference)
        self.assertEqual(manifest["project_slug"], "api_core")
        self.assertEqual(manifest["package_slug"], "auth_adapter")
        self.assertEqual(manifest["tests"][0]["args"][0], "python")
        self.assertIn("legacy_command_string_normalized", warnings)
