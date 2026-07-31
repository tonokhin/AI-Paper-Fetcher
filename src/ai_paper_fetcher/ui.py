from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .storage import load_papers
from .ui_actions import update_library_progress
from .ui_state import UiState
from .ui_views import render_index, render_logs


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
