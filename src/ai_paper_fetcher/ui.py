from __future__ import annotations

from dataclasses import dataclass
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from .config import load_tracks
from .library import move_pdf_to_status_shelf, shelf_for_status
from .models import Paper
from .progress import LearningProgress, STATUSES, load_progress, progress_path, save_progress, update_progress
from .recommendations import recommend_next_papers
from .storage import load_papers, write_papers


@dataclass
class UiState:
    data_dir: Path
    papers_dir: Path
    config_path: Path
    logs_dir: Path


def run_ui(
    data_dir: Path,
    papers_dir: Path,
    config_path: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    state = UiState(
        data_dir=data_dir,
        papers_dir=papers_dir,
        config_path=config_path,
        logs_dir=Path("logs"),
    )

    class Handler(LibraryHandler):
        ui_state = state

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Paper Fetcher UI running at http://{host}:{port}/")
    server.serve_forever()


class LibraryHandler(BaseHTTPRequestHandler):
    ui_state: UiState

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.respond_html(render_index(self.ui_state, parse_qs(parsed.query)))
            return
        if parsed.path == "/logs":
            self.respond_html(render_logs(self.ui_state, parse_qs(parsed.query)))
            return
        if parsed.path.startswith("/pdf/"):
            self.respond_pdf(unquote(parsed.path.removeprefix("/pdf/")))
            return
        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/progress":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8")
        form = {key: values[-1] for key, values in parse_qs(body).items()}
        update_library_progress(self.ui_state, form)
        self.send_response(303)
        self.send_header("Location", form.get("return_to", "/"))
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def respond_html(self, html: str) -> None:
        payload = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def respond_pdf(self, paper_id: str) -> None:
        papers = load_papers(self.ui_state.data_dir / "reading_list.csv")
        paper = next((item for item in papers if item.paper_id == paper_id), None)
        if paper is None or not paper.local_pdf_path:
            self.send_error(404)
            return

        path = Path(paper.local_pdf_path)
        if not path.exists():
            self.send_error(404)
            return

        payload = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def update_library_progress(state: UiState, form: dict[str, str]) -> None:
    paper_id = form.get("paper_id", "")
    if not paper_id:
        return

    csv_path = state.data_dir / "reading_list.csv"
    papers = load_papers(csv_path)
    progress_file = progress_path(state.data_dir)
    progress = load_progress(progress_file)

    status = form.get("status") or None
    understanding = _optional_int(form.get("understanding"))
    next_action = form.get("next_action") or None
    note = form.get("note") or None

    item = update_progress(
        progress,
        paper_id,
        status=status,
        understanding=understanding,
        next_action=next_action,
        note=note,
    )

    paper = next((candidate for candidate in papers if candidate.paper_id == paper_id), None)
    if paper is not None:
        shelf = shelf_for_status(item.status)
        if shelf is not None and move_pdf_to_status_shelf(paper, state.papers_dir, shelf) is not None:
            write_papers(csv_path, papers)

    save_progress(progress_file, progress)


def render_index(state: UiState, query: dict[str, list[str]]) -> str:
    papers = load_papers(state.data_dir / "reading_list.csv")
    progress = load_progress(progress_path(state.data_dir))
    tracks = load_tracks(state.config_path) if state.config_path.exists() else {}
    filters = {
        "q": _query_value(query, "q"),
        "status": _query_value(query, "status"),
        "track": _query_value(query, "track"),
        "topic": _query_value(query, "topic"),
        "page": _query_value(query, "page"),
        "page_size": _query_value(query, "page_size"),
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
    lines = _optional_int(_query_value(query, "lines")) or 120
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
    page_size = _bounded_int(filters.get("page_size"), default=20, minimum=1, maximum=100)
    page_count = max(1, (len(items) + page_size - 1) // page_size)
    page = _bounded_int(filters.get("page"), default=1, minimum=1, maximum=page_count)
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
    label = "Previous" if page < _bounded_int(filters.get("page"), 1, 1, 10_000) else "Next"
    return f'<a class="button" href="/?{query}">{label}</a>'


def display_topic(topic: str) -> str:
    words = topic.replace("_", " ").split()
    return " ".join(word.upper() if word.lower() in {"ai", "llm", "rag"} else word.title() for word in words)


def preview(value: str, max_chars: int = 320) -> str:
    value = " ".join(value.split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _query_value(query: dict[str, list[str]], key: str) -> str:
    return query.get(key, [""])[-1]


def _optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _bounded_int(value: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value or "")
    except ValueError:
        parsed = default
    return min(max(parsed, minimum), maximum)


CSS = """
:root {
  color-scheme: light;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f6f7f8;
  color: #1f2933;
}
body {
  margin: 0;
}
header {
  background: #ffffff;
  border-bottom: 1px solid #d9dee3;
  padding: 18px 28px;
}
h1 {
  font-size: 24px;
  margin: 0 0 4px;
}
header p {
  margin: 0;
  color: #65717c;
}
nav {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
nav a {
  color: #2457a6;
  text-decoration: none;
  font-weight: 600;
}
.filters {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) repeat(3, minmax(150px, 220px)) auto auto;
  gap: 10px;
  padding: 16px 28px;
  background: #eef1f4;
  border-bottom: 1px solid #d9dee3;
}
input, select, textarea, button, .button {
  border: 1px solid #c5ccd3;
  border-radius: 6px;
  font: inherit;
  padding: 8px 10px;
  background: #ffffff;
}
button, .button {
  background: #2457a6;
  color: #ffffff;
  text-decoration: none;
  cursor: pointer;
}
.next {
  margin: 18px 28px 0;
  padding: 14px 16px;
  background: #fff7e6;
  border: 1px solid #e5c878;
  border-radius: 8px;
}
.next h2 {
  margin: 0 0 8px;
  font-size: 16px;
}
.next p {
  margin: 6px 0 0;
}
.paper-list {
  display: grid;
  gap: 14px;
  padding: 18px 28px 32px;
}
.pagination {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 28px 0;
}
.pagination span {
  color: #65717c;
}
.paper {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
  background: #ffffff;
  border: 1px solid #d9dee3;
  border-radius: 8px;
  padding: 16px;
}
.paper h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.meta {
  color: #65717c;
  font-size: 13px;
}
.links a {
  margin-right: 12px;
}
.notes {
  color: #3f4d5a;
  font-size: 13px;
}
.progress {
  display: grid;
  gap: 10px;
  align-content: start;
}
.progress label {
  display: grid;
  gap: 4px;
  font-size: 13px;
  color: #3f4d5a;
}
.log-grid {
  display: grid;
  gap: 18px;
  padding: 18px 28px 32px;
}
.log-panel {
  background: #ffffff;
  border: 1px solid #d9dee3;
  border-radius: 8px;
  padding: 16px;
}
.log-panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
pre {
  margin: 0;
  max-height: 520px;
  overflow: auto;
  white-space: pre-wrap;
  background: #111827;
  color: #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (max-width: 900px) {
  .filters, .paper {
    grid-template-columns: 1fr;
  }
}
"""
