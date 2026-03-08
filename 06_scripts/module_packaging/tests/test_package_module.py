from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from package_module import package_workspace

class PackageModuleTests(unittest.TestCase):
    def test_workspace_is_packaged_into_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workspace = root / "workspace"
            workspace.mkdir(parents=True, exist_ok=True)
            (workspace / "src").mkdir(parents=True, exist_ok=True)
            (workspace / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
            (workspace / "manifest.json").write_text(json.dumps({
                "schema_version": "1.0",
                "project_slug": "demo_project",
                "package_slug": "demo_pkg",
                "sequence": 1,
                "package_version": "0.1.0",
                "kind": "module",
                "wiring_mode": "copy",
                "targets": [],
                "tests": [],
                "depends_on": [],
                "notes": ""
            }), encoding="utf-8")

            report_path = root / "package_report.json"
            report = package_workspace(workspace_root=workspace, repo_root=root, output_report=report_path)
            self.assertEqual(report["zip_name"], "zip1_demo_project_demo_pkg.zip")
            self.assertTrue((root / "02_modules" / "_zip_inbox" / "demo_project" / "zip1_demo_project_demo_pkg.zip").exists())
