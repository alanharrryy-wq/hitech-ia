from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from auto_ingest import auto_ingest


class AutoIngestTests(unittest.TestCase):
    def test_auto_ingest_reports_no_projects_when_inbox_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "02_modules" / "_zip_inbox").mkdir(parents=True, exist_ok=True)
            report_path = root / "ingest_report.json"
            report = auto_ingest(
                repo_root=root,
                output_report=report_path,
                mode="dry_run",
                watch=False,
                max_loops=1,
            )
            self.assertTrue(report["is_valid"])
            self.assertTrue(report["warnings"])
            self.assertEqual(report["runs"], [])
            self.assertTrue(report_path.exists())
