from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote

from .config import load_tracks
from .models import Paper
from .progress import LearningProgress, STATUSES, load_progress, progress_path
from .recommendations import recommend_next_papers
from .storage import load_papers
from .ui_state import UiState
from .ui_styles import CSS


def render_index(state: UiState, query: dict[str, list[str]]) -> str:
    papers = load_papers(state.data_dir / "reading_list.csv")
    progress = load_progress(progress_path(state.data_dir))
    tracks = load_tracks(state.config_path) if state.config_path.exists() else {}
    filters = {
        "q": query_value(query, "q"),
        "status": query_value(query, "status"),
        "track": query_value(query, "track"),
        "topic": query_value(query, "topic"),
        "page": query_value(query, "page"),
        "page_size": query_value(query, "page_size"),
    }
    visible = apply_filters(papers, progress, tracks, filters)
    pagination = pagination_for(visible, filters)
    page_papers = page_items(visible, pagination)
    recommendation = recommend_next_papers(visible, progress, limit=1)
    topics = sorted({paper.topic for paper in papers})

    return "\n".join(
        [
            "<!doctype html>",
            "<html>",
            "<head>",
            '<meta charset="utf-8">',
            "<title>AI Paper Library</title>",
            f"<style>{CSS}</style>",
            "</head>",
            "<body>",
            "<header>",
            "<h1>AI Paper Library</h1>",
            f"<p>{pagination['start_label']}-{pagination['end_label']} of {len(visible)} filtered papers, {len(papers)} total</p>",
            '<nav><a href="/">Library</a><a href="/logs">Batch Logs</a></nav>',
            "</header>",
            render_filters(filters, tracks, topics),
            render_recommendation(recommendation[0] if recommendation else None),
            render_pagination(filters, pagination),
            '<main class="paper-list">',
            *(render_paper_card(paper, progress.get(paper.paper_id), filters) for paper in page_papers),
            "</main>",
            render_pagination(filters, pagination),
            "</body>",
            "</html>",
        ]
    )


def render_logs(state: UiState, query: dict[str, list[str]]) -> str:
    lines = optional_int(query_value(query, "lines")) or 120
    lines = min(max(lines, 20), 1000)
    stdout_path = state.logs_dir / "weekly.out.log"
    stderr_path = state.logs_dir / "weekly.err.log"
    return "\n".join(
        [
            "<!doctype html>",
            "<html>",
            "<head>",
            '<meta charset="utf-8">',
            "<title>Batch Logs</title>",
            f"<style>{CSS}</style>",
            "</head>",
            "<body>",
            "<header>",
            "<h1>Batch Logs</h1>",
            "<p>Output from the scheduled paper fetch job.</p>",
            '<nav><a href="/">Library</a><a href="/logs">Batch Logs</a></nav>',
            "</header>",
            '<form class="filters" method="get" action="/logs">',
            f'<input type="number" name="lines" min="20" max="1000" value="{lines}">',
            '<button type="submit">Update</button>',
            "</form>",
            '<main class="log-grid">',
            render_log_panel("weekly.out.log", stdout_path, lines),
            render_log_panel("weekly.err.log", stderr_path, lines),
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def render_log_panel(title: str, path: Path, line_count: int) -> str:
    content = tail_text(path, line_count)
    return f"""
<section class="log-panel">
  <h2>{escape(title)}</h2>
  <p class="meta">{escape(path.as_posix())}</p>
  <pre>{escape(content)}</pre>
</section>
"""


def tail_text(path: Path, line_count: int) -> str:
    if not path.exists():
        return "No log file found yet."
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-line_count:]
    return "\n".join(tail) if tail else "Log file is empty."


def apply_filters(
    papers: list[Paper],
    progress: dict[str, LearningProgress],
    tracks: dict[str, object],
    filters: dict[str, str],
) -> list[Paper]:
    result = papers
    if filters["track"]:
        track = tracks.get(filters["track"])
        topic_names = set(getattr(track, "topics", []))
        result = [paper for paper in result if paper.topic in topic_names]
    if filters["topic"]:
        result = [paper for paper in result if paper.topic == filters["topic"]]
    if filters["status"]:
        result = [
            paper
            for paper in result
            if progress.get(paper.paper_id, LearningProgress(paper.paper_id)).status == filters["status"]
        ]
    if filters["q"]:
        needle = filters["q"].lower()
        result = [
            paper
            for paper in result
            if needle in " ".join([paper.title, paper.authors, paper.abstract, paper.topic]).lower()
        ]
    return result


def render_filters(filters: dict[str, str], tracks: dict[str, object], topics: list[str]) -> str:
    return f"""
<form class="filters" method="get" action="/">
  <input type="search" name="q" placeholder="Search papers" value="{escape(filters['q'])}">
  <input type="hidden" name="page" value="1">
  <select name="track">
    <option value="">All tracks</option>
    {''.join(option(name, filters['track']) for name in tracks)}
  </select>
  <select name="topic">
    <option value="">All topics</option>
    {''.join(option(topic, filters['topic'], display_topic(topic)) for topic in topics)}
  </select>
  <select name="status">
    <option value="">All statuses</option>
    {''.join(option(status, filters['status'], status.title()) for status in STATUSES)}
  </select>
  <select name="page_size">
    {''.join(option(str(size), filters['page_size'] or '20', str(size)) for size in [10, 20, 50, 100])}
  </select>
  <button type="submit">Filter</button>
  <a class="button" href="/">Reset</a>
</form>
"""


def render_recommendation(recommendation: object | None) -> str:
    if recommendation is None:
        return '<section class="next"><h2>Next</h2><p>No recommendation for this filter.</p></section>'
    paper = getattr(recommendation, "paper")
    reasons = "; ".join(getattr(recommendation, "reasons"))
    return f"""
<section class="next">
  <h2>Next</h2>
  <strong>{escape(paper.title)}</strong>
  <p>{escape(reasons)}</p>
</section>
"""


def render_paper_card(paper: Paper, progress: LearningProgress | None, filters: dict[str, str]) -> str:
    item = progress or LearningProgress(paper.paper_id)
    return_to = current_query(filters)
    notes = "<br>".join(escape(note) for note in item.notes[-3:])
    pdf_link = f'<a href="/pdf/{quote(paper.paper_id)}" target="_blank">Local PDF</a>' if paper.local_pdf_path else ""
    source_link = f'<a href="{escape(paper.pdf_url)}" target="_blank">arXiv PDF</a>' if paper.pdf_url else ""
    return f"""
<article class="paper">
  <div class="paper-main">
    <h2>{escape(paper.title)}</h2>
    <p class="meta">{escape(display_topic(paper.topic))} | {escape(paper.published_date or "unknown date")} | Score {escape(paper.relevance_score or "-")}</p>
    <p>{escape(preview(paper.abstract))}</p>
    <p class="links">{pdf_link} {source_link}</p>
    <p class="notes">{notes}</p>
  </div>
  <form class="progress" method="post" action="/progress">
    <input type="hidden" name="paper_id" value="{escape(paper.paper_id)}">
    <input type="hidden" name="return_to" value="{escape(return_to)}">
    <label>Status {status_select(item.status)}</label>
    <label>Understanding <input type="number" name="understanding" min="0" max="5" value="{item.understanding}"></label>
    <label>Next action <input type="text" name="next_action" value="{escape(item.next_action)}"></label>
    <label>Note <textarea name="note" rows="3"></textarea></label>
    <button type="submit">Save</button>
  </form>
</article>
"""


def status_select(current: str) -> str:
    return f'<select name="status">{"".join(option(status, current, status.title()) for status in STATUSES)}</select>'


def option(value: str, current: str, label: str | None = None) -> str:
    selected = " selected" if value == current else ""
    return f'<option value="{escape(value)}"{selected}>{escape(label or value)}</option>'


def current_query(filters: dict[str, str]) -> str:
    parts = []
    for key, value in filters.items():
        if value:
            parts.append(f"{quote(key)}={quote(value)}")
    return "/" + (("?" + "&".join(parts)) if parts else "")


def pagination_for(items: list[Paper], filters: dict[str, str]) -> dict[str, int]:
    page_size = bounded_int(filters.get("page_size"), default=20, minimum=1, maximum=100)
    page_count = max(1, (len(items) + page_size - 1) // page_size)
    page = bounded_int(filters.get("page"), default=1, minimum=1, maximum=page_count)
    start = (page - 1) * page_size
    end = min(start + page_size, len(items))
    return {
        "page": page,
        "page_size": page_size,
        "page_count": page_count,
        "start": start,
        "end": end,
        "start_label": 0 if not items else start + 1,
        "end_label": end,
    }


def page_items(items: list[Paper], pagination: dict[str, int]) -> list[Paper]:
    return items[pagination["start"] : pagination["end"]]


def render_pagination(filters: dict[str, str], pagination: dict[str, int]) -> str:
    if pagination["page_count"] <= 1:
        return ""
    page = pagination["page"]
    previous_link = pagination_link(filters, page - 1, pagination["page_size"]) if page > 1 else ""
    next_link = pagination_link(filters, page + 1, pagination["page_size"]) if page < pagination["page_count"] else ""
    return f"""
<section class="pagination">
  {previous_link}
  <span>Page {pagination['page']} of {pagination['page_count']}</span>
  {next_link}
</section>
"""


def pagination_link(filters: dict[str, str], page: int, page_size: int) -> str:
    params = {key: value for key, value in filters.items() if value and key not in {"page", "page_size"}}
    params["page"] = str(page)
    params["page_size"] = str(page_size)
    query = "&".join(f"{quote(key)}={quote(value)}" for key, value in params.items())
    label = "Previous" if page < bounded_int(filters.get("page"), 1, 1, 10_000) else "Next"
    return f'<a class="button" href="/?{query}">{label}</a>'


def display_topic(topic: str) -> str:
    words = topic.replace("_", " ").split()
    return " ".join(word.upper() if word.lower() in {"ai", "llm", "rag"} else word.title() for word in words)


def preview(value: str, max_chars: int = 320) -> str:
    value = " ".join(value.split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def query_value(query: dict[str, list[str]], key: str) -> str:
    return query.get(key, [""])[-1]


def optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def bounded_int(value: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value or "")
    except ValueError:
        parsed = default
    return min(max(parsed, minimum), maximum)
