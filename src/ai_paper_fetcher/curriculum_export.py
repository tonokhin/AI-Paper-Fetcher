from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import Paper
from .storage import load_papers


DEFAULT_ESTIMATED_HOURS = 6.0
ARXIV_ID_RE = re.compile(r"^(?P<id>\d{4}\.\d{4,5})(?:v\d+)?$")


@dataclass
class CurriculumTopicMapping:
    covers: list[str]
    stage: str = ""
    role: str = "research"


@dataclass
class CurriculumExportResult:
    written: int
    skipped_unmapped: list[str] = field(default_factory=list)


def load_curriculum_mapping(path: Path) -> dict[str, CurriculumTopicMapping]:
    if not path.exists():
        raise FileNotFoundError(f"Curriculum mapping file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    topics = raw.get("topics", {})
    if not isinstance(topics, dict):
        raise ValueError("Curriculum mapping must contain a 'topics' mapping.")

    return {
        name: _mapping_from_dict(name, value)
        for name, value in topics.items()
    }


def export_curriculum_resources(
    *,
    reading_list_path: Path,
    mapping_path: Path,
    output_path: Path,
    estimated_hours: float = DEFAULT_ESTIMATED_HOURS,
    skip_unmapped: bool = False,
) -> CurriculumExportResult:
    papers = load_papers(reading_list_path)
    mappings = load_curriculum_mapping(mapping_path)

    resources = []
    skipped: list[str] = []
    for paper in papers:
        mapping = mappings.get(paper.topic)
        if mapping is None:
            if skip_unmapped:
                skipped.append(paper.topic)
                continue
            raise ValueError(
                f"Paper '{paper.paper_id}' uses unmapped topic '{paper.topic}'. "
                "Add it to the curriculum mapping or pass --skip-unmapped."
            )
        resources.append(paper_to_resource(paper, mapping, estimated_hours=estimated_hours))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"resources": resources}
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)

    return CurriculumExportResult(
        written=len(resources),
        skipped_unmapped=sorted(set(skipped)),
    )


def paper_to_resource(
    paper: Paper,
    mapping: CurriculumTopicMapping,
    *,
    estimated_hours: float = DEFAULT_ESTIMATED_HOURS,
) -> dict[str, Any]:
    return {
        "id": resource_id_for_paper(paper),
        "title": paper.title,
        "author": paper.authors,
        "type": "paper",
        "level": "advanced",
        "cost": "free",
        "format": "text",
        "estimated_hours": float(estimated_hours),
        "url": arxiv_abs_url(paper) or paper.pdf_url,
        "covers": list(mapping.covers),
        "why": reason_to_read(paper),
        "provenance": {
            "source": "ai-paper-fetcher",
            "review_status": "pending",
        },
    }


def resource_id_for_paper(paper: Paper) -> str:
    normalized = normalize_arxiv_id(paper.paper_id) or paper.paper_id.strip()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    if not slug:
        raise ValueError(f"Paper with title '{paper.title}' has an empty paper_id.")
    return f"paper-{slug}"


def arxiv_abs_url(paper: Paper) -> str:
    arxiv_id = normalize_arxiv_id(paper.paper_id)
    return f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""


def normalize_arxiv_id(value: str) -> str:
    match = ARXIV_ID_RE.match((value or "").strip())
    return match.group("id") if match else ""


def reason_to_read(paper: Paper) -> str:
    reason = paper.reason_to_read.strip()
    if reason:
        return reason
    if paper.collection == "foundational":
        return "Foundational paper for this research area."
    return f"Research paper from the {paper.topic} topic."


def _mapping_from_dict(name: str, value: Any) -> CurriculumTopicMapping:
    if not isinstance(value, dict):
        raise ValueError(f"Curriculum mapping topic '{name}' must be a mapping.")

    covers = value.get("covers")
    if not isinstance(covers, list) or not all(isinstance(item, str) for item in covers):
        raise ValueError(f"Curriculum mapping topic '{name}' must define a 'covers' list.")

    clean_covers = [item.strip() for item in covers if item.strip()]
    if not clean_covers:
        raise ValueError(f"Curriculum mapping topic '{name}' must cover at least one concept.")

    stage = value.get("stage", "")
    role = value.get("role", "research")
    if stage is not None and not isinstance(stage, str):
        raise ValueError(f"Curriculum mapping topic '{name}' field 'stage' must be a string.")
    if role is not None and not isinstance(role, str):
        raise ValueError(f"Curriculum mapping topic '{name}' field 'role' must be a string.")

    return CurriculumTopicMapping(
        covers=clean_covers,
        stage=(stage or "").strip(),
        role=(role or "research").strip(),
    )
