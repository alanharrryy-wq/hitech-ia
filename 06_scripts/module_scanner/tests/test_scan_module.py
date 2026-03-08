from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scan_module import scan_input, write_json

class ModuleScannerTests(unittest.TestCase):
    def _make_folder_fixture(self, root: Path) -> Path:
        source = root / "source_module"
        (source / "src").mkdir(parents=True, exist_ok=True)
        (source / "tests").mkdir(parents=True, exist_ok=True)
        (source / "docs").mkdir(parents=True, exist_ok=True)
        (source / "__pycache__").mkdir(parents=True, exist_ok=True)

        (source / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
        (source / "tests" / "test_main.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        (source / "docs" / "README.md").write_text("# hello\n", encoding="utf-8")
        (source / "__pycache__" / "junk.pyc").write_bytes(b"\x00\x01")
        return source

    def _make_zip_fixture(self, root: Path) -> Path:
        zip_path = root / "raw_module.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("src/app.py", "print('zip')\n")
            zf.writestr("tests/test_app.py", "def test_zip():\n    assert True\n")
            zf.writestr("docs/README.md", "# zip\n")
            zf.writestr("__pycache__/tmp.pyc", b"abc")
            zf.writestr("../evil.txt", "bad")
        return zip_path

    def test_directory_scan_detects_python_and_noise(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self._make_folder_fixture(root)
            report = scan_input(source)
            self.assertEqual(report["input_type"], "directory")
            self.assertEqual(report["signals"]["probable_primary_language"], "python")
            self.assertTrue(report["signals"]["has_tests"])
            self.assertTrue(report["signals"]["has_docs"])
            self.assertTrue(report["signals"]["has_src"])
            self.assertGreaterEqual(report["summary"]["noise_count"], 1)
            rel_paths = [item["relative_path"] for item in report["inventory"]]
            self.assertEqual(rel_paths, sorted(rel_paths, key=str.lower))

    def test_zip_scan_emits_warning_for_unsafe_member(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            zip_path = self._make_zip_fixture(root)
            report = scan_input(zip_path)
            self.assertEqual(report["input_type"], "zip")
            self.assertTrue(report["warnings"])
            self.assertIn("Unsafe ZIP member detected: ../evil.txt", report["warnings"])
            suspicious = [item for item in report["inventory"] if item["is_suspicious"]]
            self.assertTrue(any(item["relative_path"] == "../evil.txt" for item in suspicious))

    def test_write_json_outputs_valid_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self._make_folder_fixture(root)
            report = scan_input(source)
            output_path = root / "scan_report.json"
            write_json(output_path, report)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "1.0")
            self.assertIn("summary", payload)
            self.assertIn("signals", payload)

if __name__ == "__main__":
    unittest.main()
