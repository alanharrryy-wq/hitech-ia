from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from inbox_delivery import deliver_zip
from package_layout_normalizer import iter_workspace_files, validate_workspace
from package_report import build_package_report
from sequence_allocator import canonical_zip_name, next_sequence_for_project

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def load_manifest(workspace_root: Path) -> dict:
    manifest_path = workspace_root / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))

def create_zip_from_workspace(*, workspace_root: Path, zip_path: Path) -> list[str]:
    inventory = []
    files = iter_workspace_files(workspace_root)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            rel = file_path.relative_to(workspace_root).as_posix()
            zf.write(file_path, arcname=rel)
            inventory.append(rel)
    return inventory

def package_workspace(*, workspace_root: Path, repo_root: Path, output_report: Path) -> dict:
    errors = validate_workspace(workspace_root)
    if errors:
        raise ValueError("; ".join(errors))

    manifest = load_manifest(workspace_root)
    project_slug = str(manifest["project_slug"])
    package_slug = str(manifest["package_slug"])
    sequence = next_sequence_for_project(repo_root, project_slug)
    zip_name = canonical_zip_name(sequence, project_slug, package_slug)

    warnings: list[str] = []
    if int(manifest.get("sequence", sequence)) != sequence:
        warnings.append("manifest_sequence_replaced_with_allocated_sequence")
        manifest["sequence"] = sequence
        write_json(workspace_root / "manifest.json", manifest)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_zip = Path(temp_dir) / zip_name
        inventory = create_zip_from_workspace(workspace_root=workspace_root, zip_path=temp_zip)
        delivery = deliver_zip(zip_path=temp_zip, repo_root=repo_root, project_slug=project_slug)
        final_path = Path(delivery["final_path"])
        checksum = delivery["checksum"]
        report = build_package_report(
            built_at=utc_now(),
            workspace_root=workspace_root.resolve().as_posix(),
            manifest_path=(workspace_root / "manifest.json").resolve().as_posix(),
            project_slug=project_slug,
            package_slug=package_slug,
            sequence=sequence,
            zip_name=zip_name,
            zip_size_bytes=final_path.stat().st_size,
            checksum=checksum,
            inventory=inventory,
            delivery=delivery,
            warnings=warnings,
        )
        write_json(output_report, report)
        return report

def main() -> int:
    parser = argparse.ArgumentParser(description="Package normalized module workspace into canonical inbox ZIP")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-report", required=True)
    args = parser.parse_args()

    report = package_workspace(
        workspace_root=Path(args.workspace).resolve(),
        repo_root=Path(args.repo_root).resolve(),
        output_report=Path(args.output_report).resolve(),
    )

    print("STATUS: PASS")
    print(f"zip_name: {report['zip_name']}")
    print(f"project_slug: {report['project_slug']}")
    print(f"sequence: {report['sequence']}")
    print(f"final_path: {report['delivery']['final_path']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
