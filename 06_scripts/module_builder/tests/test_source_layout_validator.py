from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from source_layout_validator import collect_usable_files

class SourceLayoutValidatorTests(unittest.TestCase):
    def test_noise_files_are_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "__pycache__").mkdir(parents=True)
            (root / "__pycache__" / "junk.pyc").write_bytes(b"abc")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
            usable = collect_usable_files(root)
            self.assertEqual([p.name for p in usable], ["app.py"])
