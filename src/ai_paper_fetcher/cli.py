from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError

from .arxiv_client import search_papers
from .downloader import download_pdf, mark_downloaded
from .models import Paper
from .storage import (
    append_papers,
    ensure_project_dirs,
    load_existing_ids,
    load_seen,
    save_seen,
)


@dataclass
class FetchSummary:
    found: int = 0
    downloaded: int = 0
    skipped_duplicates: int = 0
    failed_downloads: int = 0
    saved: int = 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "fetch"):
        if not args.topic:
            parser.error("--topic is required for fetch")
        try:
            summary = fetch(
                topic=args.topic,
                max_results=args.max_results,
                data_dir=Path(args.data_dir),
                papers_dir=Path(args.papers_dir),
                no_download=args.no_download,
            )
        except URLError as error:
            print(f"Could not reach arXiv: {error}", file=sys.stderr)
            return 1
        print_summary(summary, Path(args.data_dir) / "reading_list.csv")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-paper-fetcher",
        description="Find, download, and organize AI research papers from arXiv.",
    )
    parser.add_argument("command", nargs="?", choices=["fetch"], help="Command to run.")
    parser.add_argument("--topic", help="Topic or keyword query to search on arXiv.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum arXiv results.")
    parser.add_argument("--data-dir", default="data", help="Directory for CSV/JSON data.")
    parser.add_argument("--papers-dir", default="papers", help="Directory for downloaded PDFs.")
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Save metadata without downloading PDFs.",
    )
    return parser


def fetch(
    topic: str,
    max_results: int,
    data_dir: Path,
    papers_dir: Path,
    no_download: bool = False,
) -> FetchSummary:
    ensure_project_dirs(data_dir, papers_dir)
    reading_list_path = data_dir / "reading_list.csv"
    seen_path = data_dir / "seen_papers.json"

    seen = load_seen(seen_path)
    existing_ids = load_existing_ids(reading_list_path)
    known_ids = seen | existing_ids

    papers = search_papers(topic=topic, max_results=max_results)
    summary = FetchSummary(found=len(papers))
    new_papers: list[Paper] = []

    for paper in papers:
        if paper.paper_id in known_ids:
            summary.skipped_duplicates += 1
            continue

        if no_download:
            new_papers.append(paper)
            known_ids.add(paper.paper_id)
            seen.add(paper.paper_id)
            continue

        try:
            path = download_pdf(paper, papers_dir)
            mark_downloaded(paper, path)
            summary.downloaded += 1
        except (OSError, URLError, ValueError) as error:
            summary.failed_downloads += 1
            paper.reason_to_read = f"PDF download failed: {error}"

        new_papers.append(paper)
        known_ids.add(paper.paper_id)
        seen.add(paper.paper_id)

    append_papers(reading_list_path, new_papers)
    save_seen(seen_path, seen)
    summary.saved = len(new_papers)
    return summary


def print_summary(summary: FetchSummary, reading_list_path: Path) -> None:
    print(f"Found {summary.found} papers")
    print(f"Downloaded {summary.downloaded} new PDFs")
    print(f"Skipped {summary.skipped_duplicates} duplicates")
    if summary.failed_downloads:
        print(f"Failed to download {summary.failed_downloads} PDFs")
    print(f"Saved {summary.saved} metadata records to {reading_list_path.as_posix()}")
