from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sequence_allocator import canonical_zip_name, next_sequence_for_project

class SequenceAllocatorTests(unittest.TestCase):
    def test_next_sequence_for_existing_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_dir = root / "02_modules" / "_zip_inbox" / "alpha_proj"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "zip1_alpha_proj_core.zip").write_text("", encoding="utf-8")
            (project_dir / "zip2_alpha_proj_rules.zip").write_text("", encoding="utf-8")
            self.assertEqual(next_sequence_for_project(root, "alpha_proj"), 3)

    def test_canonical_zip_name(self) -> None:
        self.assertEqual(canonical_zip_name(4, "alpha_proj", "engine"), "zip4_alpha_proj_engine.zip")
