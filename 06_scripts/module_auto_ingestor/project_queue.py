from __future__ import annotations

from pathlib import Path


def list_candidate_projects(repo_root: Path, project_filter: str | None = None) -> list[Path]:
    inbox_root = repo_root / "02_modules" / "_zip_inbox"
    if not inbox_root.exists():
        return []
    projects = []
    for child in sorted(inbox_root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        if project_filter and child.name != project_filter:
            continue
        projects.append(child)
    return projects


def project_has_pending_zips(project_dir: Path) -> bool:
    zip_files = [p for p in project_dir.glob("*.zip") if p.is_file()]
    return len(zip_files) > 0


def build_project_queue(repo_root: Path, project_filter: str | None = None) -> list[dict]:
    queue = []
    for project_dir in list_candidate_projects(repo_root, project_filter=project_filter):
        if project_has_pending_zips(project_dir):
            queue.append(
                {
                    "project_slug": project_dir.name,
                    "project_path": project_dir.resolve().as_posix(),
                    "pending_zip_count": len(list(project_dir.glob("*.zip"))),
                }
            )
    queue.sort(key=lambda item: item["project_slug"].lower())
    return queue
