from __future__ import annotations

from pathlib import Path

def test_relpath(language: str, entrypoint_name: str) -> str:
    if language == "python":
        return f"tests/test_{entrypoint_name}.py"
    if language in {"javascript", "typescript"}:
        return f"tests/test_{entrypoint_name}.txt"
    raise ValueError(f"Unsupported language: {language}")

def build_test_content(spec: dict) -> str:
    entrypoint = spec["entrypoint_name"]
    language = spec["language"]

    if language == "python":
        return (
            f"from src.{entrypoint} import module_info\n\n"
            "def test_module_info_has_summary():\n"
            "    info = module_info()\n"
            "    assert 'summary' in info\n"
        )

    return (
        f"Placeholder test plan for {entrypoint}\n\n"
        "Validate generated module compiles and exposes expected exports.\n"
    )

def write_tests(spec: dict, workspace_root: Path) -> list[str]:
    rel = test_relpath(spec["language"], spec["entrypoint_name"])
    path = workspace_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_test_content(spec), encoding="utf-8")
    return [rel]
