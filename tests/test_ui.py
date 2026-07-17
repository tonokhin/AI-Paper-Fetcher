from __future__ import annotations

from email.message import Message
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlencode

from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.progress import LearningProgress, load_progress, progress_path
from ai_paper_fetcher.storage import load_papers, write_papers
from ai_paper_fetcher.ui import LibraryHandler, UiState, apply_filters, page_items, pagination_for


def paper(paper_id: str, title: str | None = None, topic: str = "llm_evaluation") -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title or f"Paper {paper_id}",
        authors="Ada Lovelace",
        published_date="2026-01-01",
        updated_date="2026-01-02",
        abstract=f"Abstract for {topic}",
        categories="cs.CL",
        topic=topic,
        pdf_url=f"https://arxiv.org/pdf/{paper_id}",
    )


def write_track_config(path: Path) -> None:
    path.write_text(
        """
tracks:
  ai:
    topics:
      - llm_evaluation
  fundamentals:
    topics:
      - algorithms
topics:
  llm_evaluation:
    query: "LLM evaluation"
  algorithms:
    query: "algorithms"
""",
        encoding="utf-8",
    )


def call_handler(method: str, state: UiState, path: str, body: bytes = b"") -> tuple[int, dict[str, str], bytes]:
    handler = LibraryHandler.__new__(LibraryHandler)
    handler.ui_state = state
    handler.path = path
    handler.command = method
    handler.request_version = "HTTP/1.1"
    handler.requestline = f"{method} {path} HTTP/1.1"
    handler.close_connection = True
    handler.rfile = BytesIO(body)
    handler.wfile = BytesIO()
    handler.headers = Message()
    if body:
        handler.headers["Content-Length"] = str(len(body))

    if method == "GET":
        handler.do_GET()
    elif method == "POST":
        handler.do_POST()
    else:
        raise ValueError(f"Unsupported method: {method}")

    return parse_response(handler.wfile.getvalue())


def parse_response(raw: bytes) -> tuple[int, dict[str, str], bytes]:
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").splitlines()
    status = int(lines[0].split()[1])
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key] = value.strip()
    return status, headers, body


class UiTests(unittest.TestCase):
    def test_pagination_returns_requested_page(self):
        papers = [paper(f"paper-{index:02d}") for index in range(25)]
        filters = {"page": "2", "page_size": "10"}

        pagination = pagination_for(papers, filters)
        page = page_items(papers, pagination)

        self.assertEqual(pagination["page"], 2)
        self.assertEqual(pagination["page_count"], 3)
        self.assertEqual(pagination["start_label"], 11)
        self.assertEqual(pagination["end_label"], 20)
        self.assertEqual([item.paper_id for item in page], [f"paper-{index:02d}" for index in range(10, 20)])

    def test_apply_filters_combines_track_topic_status_and_search(self):
        papers = [
            paper("paper-1", "Transformer Benchmark", "llm_evaluation"),
            paper("paper-2", "Sorting Algorithm", "algorithms"),
            paper("paper-3", "Agent Survey", "ai_agents"),
        ]
        progress = {
            "paper-1": LearningProgress(paper_id="paper-1", status="reading"),
            "paper-2": LearningProgress(paper_id="paper-2", status="skimmed"),
        }

        result = apply_filters(
            papers,
            progress,
            {
                "ai": type("Track", (), {"topics": ["llm_evaluation", "ai_agents"]})(),
                "fundamentals": type("Track", (), {"topics": ["algorithms"]})(),
            },
            {
                "track": "ai",
                "topic": "llm_evaluation",
                "status": "reading",
                "q": "benchmark",
            },
        )

        self.assertEqual([item.paper_id for item in result], ["paper-1"])

    def test_status_update_post_saves_progress_and_moves_pdf(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            papers_dir = root / "papers"
            config_path = root / "config.yaml"
            logs_dir = root / "logs"
            write_track_config(config_path)
            pdf_path = papers_dir / "llm_evaluation" / "paper.pdf"
            pdf_path.parent.mkdir(parents=True)
            pdf_path.write_bytes(b"%PDF-1.4 test")
            item = paper("paper-1")
            item.local_pdf_path = pdf_path.as_posix()
            write_papers(data_dir / "reading_list.csv", [item])
            state = UiState(data_dir=data_dir, papers_dir=papers_dir, config_path=config_path, logs_dir=logs_dir)

            request_body = urlencode(
                {
                    "paper_id": "paper-1",
                    "status": "skimmed",
                    "understanding": "2",
                    "note": "Clear motivation.",
                    "return_to": "/?status=skimmed",
                }
            ).encode("utf-8")
            status, headers, _ = call_handler("POST", state, "/progress", request_body)

            moved_path = papers_dir / "skimmed" / "llm_evaluation" / "paper.pdf"
            progress = load_progress(progress_path(data_dir))
            papers = load_papers(data_dir / "reading_list.csv")
            moved_exists = moved_path.exists()

        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], "/?status=skimmed")
        self.assertEqual(progress["paper-1"].status, "skimmed")
        self.assertEqual(progress["paper-1"].understanding, 2)
        self.assertEqual(progress["paper-1"].notes, ["Clear motivation."])
        self.assertEqual(papers[0].local_pdf_path, moved_path.as_posix())
        self.assertTrue(moved_exists)

    def test_logs_route_renders_recent_batch_logs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            papers_dir = root / "papers"
            config_path = root / "config.yaml"
            logs_dir = root / "logs"
            write_track_config(config_path)
            logs_dir.mkdir()
            (logs_dir / "weekly.out.log").write_text("\n".join(f"out-{index:02d}" for index in range(30)), encoding="utf-8")
            state = UiState(data_dir=data_dir, papers_dir=papers_dir, config_path=config_path, logs_dir=logs_dir)

            status, headers, body = call_handler("GET", state, "/logs?lines=20")
            html = body.decode("utf-8")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Batch Logs", html)
        self.assertIn("weekly.out.log", html)
        self.assertIn("out-29", html)
        self.assertNotIn("out-00", html)
        self.assertIn("No log file found yet.", html)

    def test_pdf_route_serves_local_pdf_for_paper(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            papers_dir = root / "papers"
            config_path = root / "config.yaml"
            logs_dir = root / "logs"
            write_track_config(config_path)
            pdf_path = papers_dir / "llm_evaluation" / "paper.pdf"
            pdf_path.parent.mkdir(parents=True)
            pdf_payload = b"%PDF-1.4 local paper"
            pdf_path.write_bytes(pdf_payload)
            item = paper("paper-1")
            item.local_pdf_path = pdf_path.as_posix()
            write_papers(data_dir / "reading_list.csv", [item])
            state = UiState(data_dir=data_dir, papers_dir=papers_dir, config_path=config_path, logs_dir=logs_dir)

            status, headers, payload = call_handler("GET", state, "/pdf/paper-1")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(payload, pdf_payload)


if __name__ == "__main__":
    unittest.main()
