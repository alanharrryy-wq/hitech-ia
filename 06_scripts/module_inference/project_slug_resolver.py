from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ZIP_PATTERN = re.compile(
    r"^zip(?P<sequence>[1-9][0-9]*)_(?P<project_slug>[a-z0-9]+(?:_[a-z0-9]+)*)_(?P<package_slug>[a-z0-9]+(?:_[a-z0-9]+)*)\.zip$"
)

def slugify(value: str) -> str:
    value = value.strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "new_project"

def token_overlap_score(a: str, b: str) -> float:
    tokens_a = set(token for token in a.split("_") if token)
    tokens_b = set(token for token in b.split("_") if token)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

def list_existing_projects(repo_root: Path) -> list[str]:
    inbox_root = repo_root / "02_modules" / "_zip_inbox"
    if not inbox_root.exists():
        return []
    return [
        child.name
        for child in sorted(inbox_root.iterdir(), key=lambda p: p.name.lower())
        if child.is_dir() and not child.name.startswith("_")
    ]

def next_sequence_for_project(repo_root: Path, project_slug: str) -> int:
    project_dir = repo_root / "02_modules" / "_zip_inbox" / project_slug
    if not project_dir.exists():
        return 1
    sequences = []
    for zip_path in project_dir.glob("*.zip"):
        match = ZIP_PATTERN.fullmatch(zip_path.name)
        if match:
            sequences.append(int(match.group("sequence")))
    return max(sequences) + 1 if sequences else 1

@dataclass(frozen=True)
class ProjectResolution:
    probable_project_slug: str
    resolution_mode: str
    confidence: str
    tentative_sequence: int
    candidates: list[dict]
    warnings: list[str]

def resolve_project_slug(*, repo_root: Path, source_slug: str, explicit_hint: str | None = None) -> ProjectResolution:
    warnings: list[str] = []
    existing = list_existing_projects(repo_root)
    source_slug = slugify(source_slug)

    if explicit_hint:
        hinted = slugify(explicit_hint)
        return ProjectResolution(
            probable_project_slug=hinted,
            resolution_mode="existing_project" if hinted in existing else "new_project",
            confidence="high" if hinted in existing else "medium",
            tentative_sequence=next_sequence_for_project(repo_root, hinted),
            candidates=[],
            warnings=warnings,
        )

    if source_slug in existing:
        return ProjectResolution(
            probable_project_slug=source_slug,
            resolution_mode="existing_project",
            confidence="high",
            tentative_sequence=next_sequence_for_project(repo_root, source_slug),
            candidates=[{"project_slug": source_slug, "score": 1.0}],
            warnings=warnings,
        )

    candidates = []
    for project in existing:
        score = token_overlap_score(source_slug, project)
        if score > 0:
            candidates.append({"project_slug": project, "score": round(score, 4)})
    candidates.sort(key=lambda item: (-item["score"], item["project_slug"]))

    if candidates and candidates[0]["score"] >= 0.5:
        if len(candidates) > 1 and abs(candidates[0]["score"] - candidates[1]["score"]) <= 0.1:
            warnings.append("Top project matches are close; review recommended")
            confidence = "medium"
        else:
            confidence = "high"
        chosen = candidates[0]["project_slug"]
        return ProjectResolution(
            probable_project_slug=chosen,
            resolution_mode="existing_project",
            confidence=confidence,
            tentative_sequence=next_sequence_for_project(repo_root, chosen),
            candidates=candidates[:5],
            warnings=warnings,
        )

    warnings.append("No safe existing project match; proposing new project")
    return ProjectResolution(
        probable_project_slug=source_slug,
        resolution_mode="new_project",
        confidence="medium" if source_slug != "new_project" else "low",
        tentative_sequence=1,
        candidates=candidates[:5],
        warnings=warnings,
    )
