from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from .models import Paper
from .network import ssl_context
from .text import safe_filename, slugify


def download_pdf(paper: Paper, papers_dir: Path) -> Path:
    if not paper.pdf_url:
        raise ValueError(f"No PDF URL for {paper.paper_id}")

    topic_dir = papers_dir / slugify(paper.topic)
    topic_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(f"{paper.paper_id}_{paper.title}") + ".pdf"
    destination = topic_dir / filename

    if destination.exists():
        return destination

    request = Request(paper.pdf_url, headers={"User-Agent": "ai-paper-fetcher/0.1"})
    with urlopen(request, timeout=60, context=ssl_context()) as response:
        data = response.read()

    destination.write_bytes(data)
    return destination


def mark_downloaded(paper: Paper, path: Path) -> None:
    paper.local_pdf_path = path.as_posix()
    paper.downloaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
