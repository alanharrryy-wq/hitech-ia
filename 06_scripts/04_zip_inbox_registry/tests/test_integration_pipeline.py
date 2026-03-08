from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import inbox_root_from_repo
from run_full_cycle import (
    EXIT_APPLY_FAILURE,
    EXIT_LOCK_FAILURE,
    EXIT_SUCCESS,
    EXIT_TEST_FAILURE,
    run_pipeline,
)

from helpers import create_repo_layout, create_zip_artifact, default_manifest


class IntegrationPipelineTests(unittest.TestCase):
    def test_valid_install_flow_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/feature.txt",
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest,
                file_map={"payload/content.txt": "hello-world\n"},
            )

            report, code = run_pipeline(
                repo_root=repo_root,
                inbox_root=inbox_root_from_repo(repo_root),
                project_slug="sample_project",
                run_id="20260308T100000Z_sample_project",
                mode="apply",
            )

            self.assertEqual(code, EXIT_SUCCESS)
            self.assertEqual(report["status"], "success")
            self.assertTrue((repo_root / "src" / "feature.txt").exists())
            self.assertFalse((project_dir / "zip1_sample_project_core.zip").exists())

            archive_root = repo_root / "02_modules" / "_zip_archive" / "sample_project"
            archived = list(archive_root.rglob("zip1_sample_project_core.zip"))
            self.assertEqual(len(archived), 1)
            parts = archived[0].relative_to(repo_root / "02_modules" / "_zip_archive").parts
            self.assertEqual(parts[0], "sample_project")
            self.assertEqual(len(parts), 5)

    def test_invalid_manifest_goes_to_quarantine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=99,
                target_source="payload/content.txt",
                target_destination="src/feature.txt",
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest,
            )

            report, code = run_pipeline(
                repo_root=repo_root,
                inbox_root=inbox_root_from_repo(repo_root),
                project_slug="sample_project",
                run_id="20260308T100001Z_sample_project",
                mode="apply",
            )

            self.assertEqual(code, EXIT_APPLY_FAILURE)
            self.assertIn("core", report["quarantined_packages"])
            quarantine_root = repo_root / "02_modules" / "_zip_quarantine" / "sample_project"
            quarantined = list(quarantine_root.rglob("zip1_sample_project_core.zip"))
            self.assertEqual(len(quarantined), 1)

    def test_wiring_conflict_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest1 = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/shared.txt",
            )
            manifest2 = default_manifest(
                project_slug="sample_project",
                package_slug="extension",
                sequence=2,
                target_source="payload/content.txt",
                target_destination="src/shared.txt",
            )

            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest1,
                file_map={"payload/content.txt": "first\n"},
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="extension",
                sequence=2,
                manifest=manifest2,
                file_map={"payload/content.txt": "second\n"},
            )

            report, code = run_pipeline(
                repo_root=repo_root,
                inbox_root=inbox_root_from_repo(repo_root),
                project_slug="sample_project",
                run_id="20260308T100002Z_sample_project",
                mode="apply",
            )

            self.assertEqual(code, EXIT_APPLY_FAILURE)
            self.assertEqual(report["status"], "partial_failure")
            self.assertIn("core", report["applied_packages"])
            self.assertIn("extension", report["quarantined_packages"])

    def test_required_test_failure_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_dir = create_repo_layout(repo_root)

            manifest = default_manifest(
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                target_source="payload/content.txt",
                target_destination="src/feature.txt",
                test_command='python -c "import sys; sys.exit(1)"',
            )
            create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest,
                file_map={"payload/content.txt": "rollback-me\n"},
            )

            report, code = run_pipeline(
                repo_root=repo_root,
                inbox_root=inbox_root_from_repo(repo_root),
                project_slug="sample_project",
                run_id="20260308T100003Z_sample_project",
                mode="apply",
            )

            self.assertEqual(code, EXIT_TEST_FAILURE)
            self.assertFalse((repo_root / "src" / "feature.txt").exists())
            self.assertIn("core", report["failed_packages"])
            quarantine_root = repo_root / "02_modules" / "_zip_quarantine" / "sample_project"
            self.assertEqual(len(list(quarantine_root.rglob("zip1_sample_project_core.zip"))), 1)

    def test_lock_protection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_repo_layout(repo_root)
            (repo_root / ".install.lock").write_text("busy", encoding="utf-8")

            report, code = run_pipeline(
                repo_root=repo_root,
                inbox_root=inbox_root_from_repo(repo_root),
                project_slug="sample_project",
                run_id="20260308T100004Z_sample_project",
                mode="apply",
            )

            self.assertEqual(code, EXIT_LOCK_FAILURE)
            self.assertEqual(report["status"], "failure")


if __name__ == "__main__":
    unittest.main()
