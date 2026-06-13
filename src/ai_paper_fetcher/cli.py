from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError

from .arxiv_client import search_papers
from .citations import enrich_citations
from .config import TopicConfig, load_topics
from .downloader import download_pdf, mark_downloaded
from .filtering import filter_papers
from .models import Paper
from .storage import (
    append_papers,
    ensure_project_dirs,
    load_existing_ids,
    load_papers,
    load_seen,
    save_seen,
    write_papers,
)


@dataclass
class FetchSummary:
    found: int = 0
    downloaded: int = 0
    skipped_duplicates: int = 0
    failed_downloads: int = 0
    citation_matches: int = 0
    saved: int = 0

    def add(self, other: "FetchSummary") -> None:
        self.found += other.found
        self.downloaded += other.downloaded
        self.skipped_duplicates += other.skipped_duplicates
        self.failed_downloads += other.failed_downloads
        self.citation_matches += other.citation_matches
        self.saved += other.saved


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "citations":
        try:
            updated = enrich_existing_reading_list(
                Path(args.data_dir) / "reading_list.csv",
                refresh=args.refresh_citations,
            )
        except URLError as error:
            print(f"Could not reach OpenAlex: {error}", file=sys.stderr)
            return 1

        print(f"Updated citation metadata for {updated} papers")
        print(f"Saved metadata to {(Path(args.data_dir) / 'reading_list.csv').as_posix()}")
        return 0

    if args.command in (None, "fetch"):
        try:
            summary = run_fetch(args, parser)
        except (FileNotFoundError, ValueError) as error:
            print(f"Configuration error: {error}", file=sys.stderr)
            return 1
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
    parser.add_argument("command", nargs="?", choices=["fetch", "citations"], help="Command to run.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--topic", help="Topic or keyword query to search on arXiv.")
    source.add_argument("--config-topic", help="Named topic from config.yaml.")
    source.add_argument("--all", action="store_true", dest="fetch_all", help="Fetch all configured topics.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum arXiv results.")
    parser.add_argument("--config", default="config.yaml", help="Path to topic config YAML.")
    parser.add_argument("--data-dir", default="data", help="Directory for CSV/JSON data.")
    parser.add_argument("--papers-dir", default="papers", help="Directory for downloaded PDFs.")
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Save metadata without downloading PDFs.",
    )
    parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Skip OpenAlex citation enrichment.",
    )
    parser.add_argument(
        "--refresh-citations",
        action="store_true",
        help="Refresh citation metadata even when a paper already has a citation count.",
    )
    return parser


def enrich_existing_reading_list(csv_path: Path, refresh: bool = False) -> int:
    papers = load_papers(csv_path)
    targets = [
        paper
        for paper in papers
        if refresh or not paper.citation_count
    ]
    updated = enrich_citations(targets)
    write_papers(csv_path, papers)
    return updated


def run_fetch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> FetchSummary:
    data_dir = Path(args.data_dir)
    papers_dir = Path(args.papers_dir)

    if args.topic:
        return fetch(
            topic=args.topic,
            query=args.topic,
            max_results=args.max_results,
            data_dir=data_dir,
            papers_dir=papers_dir,
            no_download=args.no_download,
            enrich_with_citations=not args.no_citations,
        )

    if args.config_topic:
        topics = load_topics(Path(args.config))
        if args.config_topic not in topics:
            parser.error(f"Unknown config topic: {args.config_topic}")
        return fetch_config_topic(
            topics[args.config_topic],
            max_results=args.max_results,
            data_dir=data_dir,
            papers_dir=papers_dir,
            no_download=args.no_download,
            enrich_with_citations=not args.no_citations,
        )

    if args.fetch_all:
        topics = load_topics(Path(args.config))
        summary = FetchSummary()
        for topic_config in topics.values():
            summary.add(
                fetch_config_topic(
                    topic_config,
                    max_results=args.max_results,
                    data_dir=data_dir,
                    papers_dir=papers_dir,
                    no_download=args.no_download,
                    enrich_with_citations=not args.no_citations,
                )
            )
        return summary

    parser.error("--topic, --config-topic, or --all is required for fetch")
    raise AssertionError("parser.error should exit")


def fetch_config_topic(
    topic_config: TopicConfig,
    max_results: int,
    data_dir: Path,
    papers_dir: Path,
    no_download: bool = False,
    enrich_with_citations: bool = True,
) -> FetchSummary:
    return fetch(
        topic=topic_config.name,
        query=topic_config.query,
        max_results=max_results,
        data_dir=data_dir,
        papers_dir=papers_dir,
        no_download=no_download,
        enrich_with_citations=enrich_with_citations,
        include_keywords=topic_config.include_keywords,
        exclude_keywords=topic_config.exclude_keywords,
        categories=topic_config.categories,
        published_after=topic_config.published_after,
    )


def fetch(
    topic: str,
    query: str,
    max_results: int,
    data_dir: Path,
    papers_dir: Path,
    no_download: bool = False,
    enrich_with_citations: bool = True,
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
    categories: list[str] | None = None,
    published_after: str | None = None,
) -> FetchSummary:
    ensure_project_dirs(data_dir, papers_dir)
    reading_list_path = data_dir / "reading_list.csv"
    seen_path = data_dir / "seen_papers.json"

    seen = load_seen(seen_path)
    existing_ids = load_existing_ids(reading_list_path)
    known_ids = seen | existing_ids

    papers = search_papers(
        query=query,
        max_results=max_results,
        topic=topic,
        categories=categories,
    )
    papers = filter_papers(
        papers,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
        published_after=published_after,
    )
    summary = FetchSummary(found=len(papers))
    new_papers: list[Paper] = []

    for paper in papers:
        if paper.paper_id in known_ids:
            summary.skipped_duplicates += 1
            continue

        if enrich_with_citations:
            summary.citation_matches += enrich_citations([paper])

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
    print(f"Matched citation metadata for {summary.citation_matches} papers")
    print(f"Saved {summary.saved} metadata records to {reading_list_path.as_posix()}")
