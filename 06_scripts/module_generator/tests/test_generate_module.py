from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from module_autodocs import write_docs
from module_autotests import write_tests
from module_skeleton import build_workspace_skeleton

class GenerateModuleTests(unittest.TestCase):
    def test_workspace_generation_creates_source_docs_and_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec = {
                "project_slug": "demo_project",
                "package_slug": "demo_pkg",
                "module_name": "Demo Package",
                "language": "python",
                "summary": "Example module",
                "features": ["alpha"],
                "exports": ["module_info"],
                "tests": [],
                "docs": ["Use responsibly"],
                "project_hint": None,
                "entrypoint_name": "demo_pkg",
            }
            skeleton = build_workspace_skeleton(spec, root / "workspace")
            docs = write_docs(spec, root / "workspace")
            tests = write_tests(spec, root / "workspace")
            self.assertEqual(skeleton["entrypoint"], "src/demo_pkg.py")
            self.assertTrue((root / "workspace" / "docs" / "README.md").exists())
            self.assertTrue((root / "workspace" / "tests" / "test_demo_pkg.py").exists())
            self.assertTrue(docs)
            self.assertTrue(tests)
