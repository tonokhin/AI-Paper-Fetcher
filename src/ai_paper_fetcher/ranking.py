from __future__ import annotations

from datetime import date, datetime

from .config import TopicConfig
from .models import Paper


HIGH_VALUE_TERMS = [
    "benchmark",
    "evaluation",
    "agent",
    "reasoning",
    "alignment",
    "interpretability",
    "multimodal",
    "tool use",
]

PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}


def rank_papers(
    papers: list[Paper],
    topics: dict[str, TopicConfig] | None = None,
    today: date | None = None,
) -> list[Paper]:
    topics = topics or {}
    today = today or date.today()

    for paper in papers:
        score_paper(paper, topics.get(paper.topic), today=today)

    return sorted(papers, key=_sort_key)


def score_paper(
    paper: Paper,
    topic_config: TopicConfig | None = None,
    today: date | None = None,
) -> int:
    today = today or date.today()
    score = 0
    matched: list[str] = []

    topic_keywords = _topic_keywords(paper, topic_config)
    title = paper.title.lower()
    abstract = paper.abstract.lower()

    for keyword in topic_keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title:
            score += 5
            matched.append(keyword)
        elif keyword_lower in abstract:
            score += 3
            matched.append(keyword)

    for term in HIGH_VALUE_TERMS:
        term_lower = term.lower()
        if term_lower in title:
            score += 3
            matched.append(term)
        elif term_lower in abstract:
            score += 2
            matched.append(term)

    recency_score = _recency_score(paper.published_date, today)
    score += recency_score
    if recency_score:
        matched.append("recent")

    citation_score = _citation_score(paper.citation_count)
    score += citation_score
    if citation_score:
        matched.append("cited")

    for keyword in _exclude_keywords(topic_config):
        if keyword.lower() in title or keyword.lower() in abstract:
            score -= 6
            matched.append(f"excluded:{keyword}")

    paper.relevance_score = str(score)
    paper.matched_keywords = ", ".join(_unique(matched))
    paper.priority = priority_for_score(score)
    paper.reason_to_read = reason_to_read(paper)
    return score


def priority_for_score(score: int) -> str:
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def reason_to_read(paper: Paper) -> str:
    matched = [item for item in paper.matched_keywords.split(", ") if item]
    if matched:
        terms = ", ".join(matched[:4])
        return f"Matches {terms}."
    return "Low keyword match; inspect manually before prioritizing."


def _topic_keywords(paper: Paper, topic_config: TopicConfig | None) -> list[str]:
    if topic_config and topic_config.include_keywords:
        return topic_config.include_keywords
    return [part for part in paper.topic.replace("_", " ").split() if part]


def _exclude_keywords(topic_config: TopicConfig | None) -> list[str]:
    if not topic_config:
        return []
    return topic_config.exclude_keywords


def _recency_score(published_date: str, today: date) -> int:
    if not published_date:
        return 0

    try:
        published = datetime.strptime(published_date, "%Y-%m-%d").date()
    except ValueError:
        return 0

    age_days = (today - published).days
    if age_days < 0:
        return 0
    if age_days <= 30:
        return 2
    if age_days <= 90:
        return 1
    return 0


def _citation_score(citation_count: str) -> int:
    try:
        count = int(citation_count)
    except (TypeError, ValueError):
        return 0

    if count >= 100:
        return 3
    if count >= 25:
        return 2
    if count >= 5:
        return 1
    return 0


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        normalized = value.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(value)
    return unique_values


def _sort_key(paper: Paper) -> tuple[int, int, int, str]:
    try:
        score = int(paper.relevance_score)
    except ValueError:
        score = 0
    try:
        citations = int(paper.citation_count)
    except ValueError:
        citations = 0

    return (
        PRIORITY_ORDER.get(paper.priority, 3),
        -score,
        -citations,
        paper.published_date,
    )
