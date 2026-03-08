from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inbox_delivery import deliver_zip

class InboxDeliveryTests(unittest.TestCase):
    def test_delivery_moves_zip_into_project_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_zip = root / "tmp.zip"
            source_zip.write_bytes(b"abc")
            result = deliver_zip(zip_path=source_zip, repo_root=root, project_slug="demo")
            self.assertEqual(result["delivery_result"], "moved")
            self.assertTrue((root / "02_modules" / "_zip_inbox" / "demo" / "tmp.zip").exists())
