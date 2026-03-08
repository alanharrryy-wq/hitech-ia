from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_slug_resolver import next_sequence_for_project, resolve_project_slug

class ProjectSlugResolverTests(unittest.TestCase):
    def test_exact_project_match_returns_existing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_dir = root / "02_modules" / "_zip_inbox" / "ui_observability"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "zip1_ui_observability_core.zip").write_text("", encoding="utf-8")

            resolution = resolve_project_slug(repo_root=root, source_slug="ui_observability", explicit_hint=None)
            self.assertEqual(resolution.probable_project_slug, "ui_observability")
            self.assertEqual(resolution.resolution_mode, "existing_project")
            self.assertEqual(resolution.tentative_sequence, 2)

    def test_explicit_hint_can_create_new_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "02_modules" / "_zip_inbox").mkdir(parents=True, exist_ok=True)
            resolution = resolve_project_slug(repo_root=root, source_slug="whatever", explicit_hint="fresh_stack")
            self.assertEqual(resolution.probable_project_slug, "fresh_stack")
            self.assertEqual(resolution.resolution_mode, "new_project")
            self.assertEqual(resolution.tentative_sequence, 1)

    def test_next_sequence_for_project_reads_existing_zips(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_dir = root / "02_modules" / "_zip_inbox" / "api_core"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "zip1_api_core_base.zip").write_text("", encoding="utf-8")
            (project_dir / "zip2_api_core_auth.zip").write_text("", encoding="utf-8")
            self.assertEqual(next_sequence_for_project(root, "api_core"), 3)
