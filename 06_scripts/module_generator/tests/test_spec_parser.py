from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from spec_parser import normalize_module_spec

class SpecParserTests(unittest.TestCase):
    def test_normalize_minimal_python_spec(self) -> None:
        spec, warnings = normalize_module_spec({
            "project_slug": "Demo Project",
            "package_slug": "My Package",
            "module_name": "My Package",
            "language": "python",
            "summary": "A useful module",
        })
        self.assertEqual(spec["project_slug"], "demo_project")
        self.assertEqual(spec["package_slug"], "my_package")
        self.assertEqual(spec["entrypoint_name"], "my_package")
        self.assertFalse(warnings)

    def test_unsupported_language_fails(self) -> None:
        with self.assertRaises(ValueError):
            normalize_module_spec({
                "project_slug": "demo",
                "package_slug": "pkg",
                "module_name": "Pkg",
                "language": "brainfuck",
                "summary": "oops",
            })
