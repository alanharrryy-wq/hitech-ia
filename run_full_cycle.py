from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path


def _load_runtime_module(wrapper_root: Path):
    runtime_dir = wrapper_root / "06_scripts" / "04_zip_inbox_registry"
    runtime_script = runtime_dir / "run_full_cycle.py"
    if str(runtime_dir) not in sys.path:
        sys.path.insert(0, str(runtime_dir))

    spec = importlib.util.spec_from_file_location("zip_inbox_runtime_run_full_cycle", runtime_script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load runtime script: {runtime_script}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="One-command ZIP inbox full cycle wrapper")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--inbox-root", help="Optional inbox root override")
    parser.add_argument("--run-id", help="Optional deterministic run id")
    parser.add_argument("--mode", choices=["apply", "dry_run"], default="apply")
    args = parser.parse_args()

    wrapper_root = Path(__file__).resolve().parent
    runtime = _load_runtime_module(wrapper_root)

    common = importlib.import_module("common")
    resolved_repo_root = common.repo_root_from_arg(args.repo_root)
    inbox_root = common.resolve_inbox_root(resolved_repo_root, args.inbox_root)

    report, code = runtime.run_pipeline(
        repo_root=resolved_repo_root,
        inbox_root=inbox_root,
        project_slug=args.project,
        run_id=args.run_id,
        mode=args.mode,
    )

    print("STATUS:", "PASS" if code == 0 else "FAIL")
    print(f"run_id: {report['run_id']}")
    print(f"project: {report['project_slug']}")
    print(f"report_status: {report['status']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
