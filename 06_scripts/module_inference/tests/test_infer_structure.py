from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from infer_structure import infer_structure

class InferStructureTests(unittest.TestCase):
    def _make_repo(self, root: Path) -> None:
        inbox = root / "02_modules" / "_zip_inbox" / "ui_observability"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "zip1_ui_observability_core.zip").write_text("", encoding="utf-8")

    def test_existing_project_and_targets_are_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._make_repo(root)
            scan_report = {
                "input_path": "/tmp/ui_observability_panel.zip",
                "signals": {
                    "probable_primary_language": "python",
                    "language_counts": {"python": 2},
                    "has_src": True, "has_docs": True, "has_tests": True
                },
                "inventory": [
                    {"relative_path": "src/panel.py", "is_noise": False, "is_suspicious": False, "is_textish": True},
                    {"relative_path": "tests/test_panel.py", "is_noise": False, "is_suspicious": False, "is_textish": True},
                    {"relative_path": "docs/README.md", "is_noise": False, "is_suspicious": False, "is_textish": True},
                ],
            }
            report = infer_structure(
                scan_report=scan_report,
                repo_root=root,
                scan_report_path="/tmp/scan_report.json",
                project_hint=None,
            )
            self.assertEqual(report["probable_project_slug"], "ui_observability")
            self.assertEqual(report["project_resolution"]["resolution_mode"], "existing_project")
            self.assertEqual(report["project_resolution"]["tentative_sequence"], 2)
            self.assertTrue(report["target_suggestions"])

    def test_new_project_falls_back_to_sequence_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "02_modules" / "_zip_inbox").mkdir(parents=True, exist_ok=True)
            scan_report = {
                "input_path": "/tmp/new_feature_bundle.zip",
                "signals": {"probable_primary_language": "typescript", "language_counts": {"typescript": 1}},
                "inventory": [
                    {"relative_path": "src/widget.tsx", "is_noise": False, "is_suspicious": False, "is_textish": True},
                ],
            }
            report = infer_structure(
                scan_report=scan_report,
                repo_root=root,
                scan_report_path="/tmp/scan_report.json",
                project_hint=None,
            )
            self.assertEqual(report["project_resolution"]["resolution_mode"], "new_project")
            self.assertEqual(report["project_resolution"]["tentative_sequence"], 1)
            self.assertTrue(report["probable_project_slug"])
