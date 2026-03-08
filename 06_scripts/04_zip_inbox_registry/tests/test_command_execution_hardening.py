from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import ValidationError, ZipArtifact
from manifest_validator import validate_and_normalize_manifest
from test_executor import TIMEOUT_EXIT_CODE, run_manifest_tests

from helpers import create_repo_layout, create_zip_artifact, default_manifest


class CommandExecutionHardeningTests(unittest.TestCase):
    def test_structured_args_and_env_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            logs_dir = repo_root / "logs"

            tests = [
                {
                    "name": "env_args",
                    "type": "command",
                    "args": [
                        sys.executable,
                        "-c",
                        "import os,sys; sys.exit(0 if os.environ.get('ZIP_FLAG') == '1' else 5)",
                    ],
                    "cwd": ".",
                    "timeout_sec": 30,
                    "env": {"ZIP_FLAG": "1"},
                    "required": True,
                }
            ]

            records, required_failed = run_manifest_tests(
                tests,
                repo_root=repo_root,
                logs_dir=logs_dir,
                package_slug="core",
            )

            self.assertFalse(required_failed)
            self.assertEqual(records[0]["status"], "passed")
            self.assertEqual(records[0]["exit_code"], 0)

    def test_timeout_returns_failed_record_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            logs_dir = repo_root / "logs"

            tests = [
                {
                    "name": "timeout_case",
                    "type": "command",
                    "args": [
                        sys.executable,
                        "-c",
                        "import time; time.sleep(2)",
                    ],
                    "cwd": ".",
                    "timeout_sec": 1,
                    "env": {},
                    "required": True,
                }
            ]

            records, required_failed = run_manifest_tests(
                tests,
                repo_root=repo_root,
                logs_dir=logs_dir,
                package_slug="core",
            )

            self.assertTrue(required_failed)
            self.assertEqual(records[0]["status"], "failed")
            self.assertEqual(records[0]["exit_code"], TIMEOUT_EXIT_CODE)

    def test_manifest_rejects_unsafe_cwd(self) -> None:
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
            manifest["tests"][0]["args"] = [sys.executable, "-c", "print('ok')"]
            manifest["tests"][0].pop("command", None)
            manifest["tests"][0]["cwd"] = "../outside"

            zip_path = create_zip_artifact(
                project_dir=project_dir,
                project_slug="sample_project",
                package_slug="core",
                sequence=1,
                manifest=manifest,
                file_map={"payload/content.txt": "hello-world\n"},
            )

            extracted_root = repo_root / "extracted"
            extracted_root.mkdir(parents=True, exist_ok=True)
            (extracted_root / "manifest.json").write_text(
                json.dumps(manifest, indent=2),
                encoding="utf-8",
            )
            payload_dir = extracted_root / "payload"
            payload_dir.mkdir(parents=True, exist_ok=True)
            (payload_dir / "content.txt").write_text("hello-world\n", encoding="utf-8")

            artifact = ZipArtifact(
                filename=zip_path.name,
                sequence=1,
                project_slug="sample_project",
                package_slug="core",
                path=zip_path,
                relative_path="sample_project/" + zip_path.name,
                sha256="deadbeef",
                size_bytes=zip_path.stat().st_size,
            )

            with self.assertRaises(ValidationError):
                validate_and_normalize_manifest(
                    manifest,
                    artifact=artifact,
                    extracted_root=extracted_root,
                    repo_root=repo_root,
                )


if __name__ == "__main__":
    unittest.main()
