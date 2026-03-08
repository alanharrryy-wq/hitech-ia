from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import create_repo_layout, create_zip_artifact, default_manifest


class SmokeWrapperTests(unittest.TestCase):
    def test_one_command_wrapper_runs_end_to_end(self) -> None:
        wrapper_repo_root = Path(__file__).resolve().parents[3]
        wrapper_script = wrapper_repo_root / "run_full_cycle.py"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo_root = Path(temp_dir)
            project_dir = create_repo_layout(temp_repo_root)

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
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(wrapper_script),
                    "--project",
                    "sample_project",
                    "--repo-root",
                    str(temp_repo_root),
                    "--run-id",
                    "smoke_wrapper_run",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stdout + "\n" + completed.stderr)
            report_path = (
                temp_repo_root
                / "05_reports"
                / "zip_inbox"
                / "sample_project"
                / "smoke_wrapper_run"
                / "report.json"
            )
            self.assertTrue(report_path.exists())


if __name__ == "__main__":
    unittest.main()
