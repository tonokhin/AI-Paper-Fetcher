from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .models import Paper


PRIORITIES = ["High", "Medium", "Low", ""]


def write_markdown_report(papers: list[Paper], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(papers), encoding="utf-8")


def render_markdown_report(papers: list[Paper]) -> str:
    lines = [
        "# AI Paper Reading List",
        "",
        f"Total papers: {len(papers)}",
        "",
    ]

    if not papers:
        lines.extend(["No papers found yet.", ""])
        return "\n".join(lines)

    grouped = _group_by_priority(papers)
    for priority in PRIORITIES:
        priority_papers = grouped.get(priority, [])
        if not priority_papers:
            continue

        heading = priority or "Unranked"
        lines.extend([f"## {heading} Priority", ""])

        by_topic = _group_by_topic(priority_papers)
        for topic, topic_papers in by_topic.items():
            lines.extend([f"### {topic}", ""])
            for paper in topic_papers:
                lines.extend(_paper_lines(paper))

    return "\n".join(lines).rstrip() + "\n"


def _group_by_priority(papers: list[Paper]) -> dict[str, list[Paper]]:
    grouped: dict[str, list[Paper]] = defaultdict(list)
    for paper in papers:
        grouped[paper.priority].append(paper)
    return grouped


def _group_by_topic(papers: list[Paper]) -> dict[str, list[Paper]]:
    grouped: dict[str, list[Paper]] = defaultdict(list)
    for paper in papers:
        grouped[_display_topic(paper.topic)].append(paper)
    return dict(sorted(grouped.items(), key=lambda item: item[0]))


def _paper_lines(paper: Paper) -> list[str]:
    lines = [
        f"#### {_escape_markdown_heading(paper.title)}",
        "",
        f"- Score: {_value_or_dash(paper.relevance_score)}",
        f"- Citations: {_value_or_dash(paper.citation_count)}",
        f"- Published: {_value_or_dash(paper.published_date)}",
        f"- Authors: {_value_or_dash(paper.authors)}",
        f"- Why read it: {_value_or_dash(paper.reason_to_read)}",
    ]

    if paper.matched_keywords:
        lines.append(f"- Matched keywords: {paper.matched_keywords}")

    abstract = _abstract_preview(paper.abstract)
    if abstract:
        lines.append(f"- Abstract: {abstract}")

    for label, url in _links(paper):
        lines.append(f"- {label}: {url}")

    lines.append("")
    return lines


def _links(paper: Paper) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    if paper.local_pdf_path:
        links.append(("Local PDF", paper.local_pdf_path))
    elif paper.pdf_url:
        links.append(("PDF", paper.pdf_url))
    if paper.pdf_url:
        links.append(("arXiv PDF", paper.pdf_url))
    if paper.openalex_id:
        links.append(("OpenAlex", paper.openalex_id))
    return links


def _abstract_preview(abstract: str, max_chars: int = 500) -> str:
    abstract = " ".join(abstract.split())
    if len(abstract) <= max_chars:
        return abstract
    return abstract[: max_chars - 3].rstrip() + "..."


def _display_topic(topic: str) -> str:
    words = topic.replace("_", " ").strip().split()
    if not words:
        return "Uncategorized"
    return " ".join(_display_word(word) for word in words)


def _display_word(word: str) -> str:
    acronyms = {
        "ai": "AI",
        "llm": "LLM",
        "rlhf": "RLHF",
    }
    return acronyms.get(word.lower(), word.title())


def _value_or_dash(value: str) -> str:
    return value if value else "-"


def _escape_markdown_heading(value: str) -> str:
    return value.replace("\n", " ").strip()
