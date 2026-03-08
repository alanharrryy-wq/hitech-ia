from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from module_workspace_builder import build_workspace
from source_layout_validator import validate_source_layout

class BuildModuleTests(unittest.TestCase):
    def test_workspace_builder_normalizes_into_canonical_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            (source / "docs").mkdir()
            (source / "tests").mkdir()
            (source / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (source / "docs" / "README.md").write_text("# hi\n", encoding="utf-8")
            (source / "tests" / "test_main.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

            workspace = root / "workspace"
            result = build_workspace(source, workspace)
            self.assertTrue((workspace / "assets" / "main.py").exists())
            self.assertTrue((workspace / "docs" / "README.md").exists())
            self.assertTrue((workspace / "tests" / "test_main.py").exists())
            self.assertFalse(result["collision_paths"])

    def test_source_validator_rejects_empty_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "empty"
            source.mkdir()
            errors = validate_source_layout(source)
            self.assertTrue(errors)
