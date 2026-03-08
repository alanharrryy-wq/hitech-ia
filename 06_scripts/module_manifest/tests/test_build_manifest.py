from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_manifest import build_manifest

class BuildManifestTests(unittest.TestCase):
    def test_build_manifest_from_inference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inference = {
                "probable_project_slug": "ui_observability",
                "probable_package_slug": "ui_panel",
                "project_resolution": {"tentative_sequence": 2},
                "target_suggestions": [
                    {"source": "src/panel.py", "destination": "src/panel.py", "required": True, "reason": "deterministic_path_mapping"},
                    {"source": "docs/README.md", "destination": "docs/README.md", "required": True, "reason": "deterministic_path_mapping"},
                ],
            }
            inference_path = root / "inference_report.json"
            inference_path.write_text(json.dumps(inference), encoding="utf-8")

            output_manifest = root / "manifest.json"
            output_report = root / "manifest_report.json"
            report = build_manifest(
                inference_report_path=inference_path,
                output_manifest_path=output_manifest,
                output_report_path=output_report,
                existing_manifest_path=None,
            )

            manifest = json.loads(output_manifest.read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_slug"], "ui_observability")
            self.assertEqual(manifest["package_slug"], "ui_panel")
            self.assertEqual(manifest["sequence"], 2)
            self.assertTrue(report["is_valid"])
