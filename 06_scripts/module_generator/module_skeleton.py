from __future__ import annotations

from pathlib import Path

def source_relpath(language: str, entrypoint_name: str) -> str:
    if language == "python":
        return f"src/{entrypoint_name}.py"
    if language == "javascript":
        return f"src/{entrypoint_name}.js"
    if language == "typescript":
        return f"src/{entrypoint_name}.ts"
    raise ValueError(f"Unsupported language: {language}")

def build_source_code(spec: dict) -> str:
    module_name = spec["module_name"]
    summary = spec["summary"]
    features = spec.get("features", [])
    language = spec["language"]

    if language == "python":
        return (
            '# Auto-generated module scaffold\n'
            f'# {module_name}\n'
            f'# {summary}\n\n'
            'def module_info() -> dict:\n'
            '    return {\n'
            f'        "module_name": "{module_name}",\n'
            f'        "summary": "{summary}",\n'
            f'        "features": {features!r},\n'
            '    }\n\n'
            'def main() -> None:\n'
            '    info = module_info()\n'
            '    print(f"{info[\'module_name\']}: {info[\'summary\']}")\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        )

    if language == "javascript":
        return (
            f'// {module_name}\n'
            f'// {summary}\n\n'
            'function moduleInfo() {\n'
            '  return {\n'
            f'    moduleName: "{module_name}",\n'
            f'    summary: "{summary}",\n'
            f'    features: {features!r},\n'
            '  };\n'
            '}\n\n'
            'function main() {\n'
            '  const info = moduleInfo();\n'
            '  console.log(`${info.moduleName}: ${info.summary}`);\n'
            '}\n\n'
            'module.exports = { moduleInfo, main };\n'
        )

    if language == "typescript":
        return (
            'export type ModuleInfo = { moduleName: string; summary: string; features: string[] };\n\n'
            'export function moduleInfo(): ModuleInfo {\n'
            '  return {\n'
            f'    moduleName: "{module_name}",\n'
            f'    summary: "{summary}",\n'
            f'    features: {features!r} as string[],\n'
            '  };\n'
            '}\n\n'
            'export function main(): void {\n'
            '  const info = moduleInfo();\n'
            '  console.log(`${info.moduleName}: ${info.summary}`);\n'
            '}\n'
        )

    raise ValueError(f"Unsupported language: {language}")

def build_workspace_skeleton(spec: dict, workspace_root: Path) -> dict:
    workspace_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    for rel in ["src", "tests", "docs", "config"]:
        path = workspace_root / rel
        path.mkdir(parents=True, exist_ok=True)
        created.append(f"{rel}/")

    src_rel = source_relpath(spec["language"], spec["entrypoint_name"])
    src_path = workspace_root / src_rel
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text(build_source_code(spec), encoding="utf-8")
    created.append(src_rel)

    return {
        "workspace_root": workspace_root.resolve().as_posix(),
        "entrypoint": src_rel,
        "created": created,
    }
