from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_queue import build_project_queue


class ProjectQueueTests(unittest.TestCase):
    def test_build_project_queue_detects_pending_zip_projects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = root / "02_modules" / "_zip_inbox" / "alpha_proj"
            beta = root / "02_modules" / "_zip_inbox" / "beta_proj"
            alpha.mkdir(parents=True, exist_ok=True)
            beta.mkdir(parents=True, exist_ok=True)
            (alpha / "zip1_alpha_proj_core.zip").write_text("", encoding="utf-8")

            queue = build_project_queue(root)
            self.assertEqual(len(queue), 1)
            self.assertEqual(queue[0]["project_slug"], "alpha_proj")
            self.assertEqual(queue[0]["pending_zip_count"], 1)
