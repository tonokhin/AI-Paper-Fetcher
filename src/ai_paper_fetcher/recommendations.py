from __future__ import annotations

from dataclasses import dataclass
from math import log10

from .models import Paper
from .progress import LearningProgress


DONE_STATUSES = {"understood", "archived"}


@dataclass
class Recommendation:
    paper: Paper
    score: float
    reasons: list[str]
    progress: LearningProgress | None = None


def recommend_next_papers(
    papers: list[Paper],
    progress: dict[str, LearningProgress],
    limit: int = 1,
) -> list[Recommendation]:
    recommendations = [
        score_next_paper(paper, progress.get(paper.paper_id))
        for paper in papers
        if _is_candidate(progress.get(paper.paper_id))
    ]
    recommendations.sort(key=lambda item: (-item.score, _reading_list_position(papers, item.paper)))
    return recommendations[: max(1, limit)]


def score_next_paper(paper: Paper, progress: LearningProgress | None = None) -> Recommendation:
    score = 0.0
    reasons: list[str] = []

    relevance = _int_value(paper.relevance_score)
    if relevance:
        score += relevance * 2
        reasons.append(f"relevance score {relevance}")

    citation_count = _int_value(paper.citation_count)
    if citation_count:
        citation_score = log10(citation_count + 1) * 8
        score += citation_score
        reasons.append(f"{citation_count} citations")
    elif paper.openalex_id:
        score += 2
        reasons.append("has OpenAlex graph metadata")

    if paper.collection == "foundational":
        score += 12
        reasons.append("foundational paper")

    if paper.local_pdf_path:
        score += 3
        reasons.append("PDF is already downloaded")

    if progress is None:
        score += 8
        reasons.append("not started")
    else:
        progress_score, progress_reason = _progress_score(progress)
        score += progress_score
        reasons.append(progress_reason)
        if progress.next_action:
            score += 4
            reasons.append(f"next action: {progress.next_action}")

    return Recommendation(paper=paper, score=score, reasons=reasons, progress=progress)


def _is_candidate(progress: LearningProgress | None) -> bool:
    return progress is None or progress.status not in DONE_STATUSES


def _progress_score(progress: LearningProgress) -> tuple[float, str]:
    if progress.status == "reading":
        return 24 + (5 - progress.understanding) * 3, f"currently reading, understanding {progress.understanding}/5"
    if progress.status == "skimmed":
        return 14 + (5 - progress.understanding) * 2, f"skimmed, understanding {progress.understanding}/5"
    if progress.status == "queued":
        return 8 + (5 - progress.understanding), f"queued, understanding {progress.understanding}/5"
    return 4, f"{progress.status}, understanding {progress.understanding}/5"


def _int_value(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _reading_list_position(papers: list[Paper], target: Paper) -> int:
    for index, paper in enumerate(papers):
        if paper.paper_id == target.paper_id:
            return index
    return len(papers)
