from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from safe_extractor import inspect_zip_paths
from validate_inbox import build_validation_report

from helpers import create_repo_layout, create_zip_artifact, default_manifest


class UnitValidationTests(unittest.TestCase):
    def test_sequence_gap_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest1 = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/core.txt",
            )
            manifest3 = default_manifest(
                project_slug="sample_project",
                package_slug="extra",
                sequence=3,
                target_source="payload/content.txt",
                target_destination="src/extra.txt",
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest1,
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="extra",
                sequence=3,
                manifest=manifest3,
            )

            report = build_validation_report(repo_root / "02_modules" / "_zip_inbox", "sample_project")
            self.assertFalse(report["valid"])
            self.assertEqual(report["projects"][0]["sequence_status"]["missing_sequences"], [2])

    def test_duplicate_sequence_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest1 = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/core.txt",
            )
            manifest1b = default_manifest(
                project_slug="sample_project",
                package_slug="extra",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/extra.txt",
            )

            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest1,
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="extra",
                sequence=1,
                manifest=manifest1b,
            )

            report = build_validation_report(repo_root / "02_modules" / "_zip_inbox", "sample_project")
            self.assertFalse(report["valid"])
            self.assertEqual(report["projects"][0]["sequence_status"]["duplicate_sequences"], [1])

    def test_unsafe_zip_path_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/core.txt",
            )
            zip_path = create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest,
                unsafe_entries={"../evil.txt": "owned"},
            )

            safe_entries, errors = inspect_zip_paths(zip_path)
            self.assertTrue(errors)
            self.assertIn("manifest.json", safe_entries)


if __name__ == "__main__":
    unittest.main()
