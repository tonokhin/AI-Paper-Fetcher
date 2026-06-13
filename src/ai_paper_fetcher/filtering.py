from __future__ import annotations

from .models import Paper


def filter_papers(
    papers: list[Paper],
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
    published_after: str | None = None,
) -> list[Paper]:
    include_keywords = include_keywords or []
    exclude_keywords = exclude_keywords or []

    return [
        paper
        for paper in papers
        if _matches_include(paper, include_keywords)
        and not _matches_exclude(paper, exclude_keywords)
        and _matches_date(paper, published_after)
    ]


def _matches_include(paper: Paper, keywords: list[str]) -> bool:
    if not keywords:
        return True
    searchable = _searchable_text(paper)
    return any(keyword.lower() in searchable for keyword in keywords)


def _matches_exclude(paper: Paper, keywords: list[str]) -> bool:
    searchable = _searchable_text(paper)
    return any(keyword.lower() in searchable for keyword in keywords)


def _matches_date(paper: Paper, published_after: str | None) -> bool:
    if not published_after:
        return True
    return bool(paper.published_date and paper.published_date >= published_after)


def _searchable_text(paper: Paper) -> str:
    return f"{paper.title} {paper.abstract}".lower()
