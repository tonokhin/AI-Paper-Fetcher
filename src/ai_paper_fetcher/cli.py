from __future__ import annotations

import argparse
import sys
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError

from .arxiv_client import search_papers
from .citations import enrich_citations
from .config import TopicConfig, load_topics
from .downloader import download_pdf, mark_downloaded
from .filtering import filter_papers
from .models import Paper
from .ranking import rank_papers
from .reporting import write_markdown_report
from .storage import (
    append_papers,
    ensure_project_dirs,
    load_existing_ids,
    load_papers,
    load_seen,
    save_seen,
    write_papers,
)


class Progress:
    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet

    def log(self, message: str) -> None:
        if not self.quiet:
            print(message, file=sys.stderr, flush=True)


@dataclass
class FetchSummary:
    found: int = 0
    downloaded: int = 0
    skipped_duplicates: int = 0
    failed_downloads: int = 0
    citation_matches: int = 0
    saved: int = 0
    ranked: int = 0
    pages_searched: int = 0

    def add(self, other: "FetchSummary") -> None:
        self.found += other.found
        self.downloaded += other.downloaded
        self.skipped_duplicates += other.skipped_duplicates
        self.failed_downloads += other.failed_downloads
        self.citation_matches += other.citation_matches
        self.saved += other.saved
        self.ranked += other.ranked
        self.pages_searched += other.pages_searched


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "weekly":
        try:
            result = run_weekly(args)
        except (FileNotFoundError, ValueError) as error:
            print(f"Weekly run error: {error}", file=sys.stderr)
            return 1
        except URLError as error:
            print(f"Could not reach arXiv or OpenAlex: {error}", file=sys.stderr)
            return 1

        print_summary(result.summary, Path(args.data_dir) / "reading_list.csv")
        print(f"Generated report for {result.report_count} papers")
        print(f"Saved report to {result.reading_list_report_path.as_posix()}")
        print(f"Saved weekly report to {result.weekly_report_path.as_posix()}")
        return 0

    if args.command == "report":
        output_path = Path(args.report_path) if args.report_path else Path(args.data_dir) / "reading_list.md"
        count = generate_report(Path(args.data_dir) / "reading_list.csv", output_path)
        print(f"Generated report for {count} papers")
        print(f"Saved report to {output_path.as_posix()}")
        return 0

    if args.command == "rank":
        try:
            count = rank_existing_reading_list(
                Path(args.data_dir) / "reading_list.csv",
                Path(args.config),
            )
        except (FileNotFoundError, ValueError) as error:
            print(f"Ranking error: {error}", file=sys.stderr)
            return 1

        print(f"Ranked {count} papers")
        print(f"Saved ranked reading list to {(Path(args.data_dir) / 'reading_list.csv').as_posix()}")
        return 0

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
    parser.add_argument(
        "command",
        nargs="?",
        choices=["fetch", "citations", "rank", "report", "weekly"],
        help="Command to run.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--topic", help="Topic or keyword query to search on arXiv.")
    source.add_argument("--config-topic", help="Named topic from config.yaml.")
    source.add_argument("--all", action="store_true", dest="fetch_all", help="Fetch all configured topics.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum arXiv results.")
    parser.add_argument(
        "--new-results",
        action="store_true",
        help="Keep searching until max-results new papers are saved, or max-pages is reached. Weekly enables this by default.",
    )
    parser.add_argument(
        "--no-new-results",
        action="store_true",
        help="Disable weekly's default behavior of paging until new papers are found.",
    )
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum arXiv pages to inspect with --new-results.")
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
    parser.add_argument(
        "--no-rank",
        action="store_true",
        help="Skip automatic ranking after fetch.",
    )
    parser.add_argument("--report-path", help="Output path for the Markdown report.")
    parser.add_argument(
        "--weekly-reports-dir",
        default="weekly_reports",
        help="Directory for dated weekly Markdown reports.",
    )
    parser.add_argument(
        "--report-date",
        help="Date to use for weekly report filename, in YYYY-MM-DD format.",
    )
    parser.add_argument("--quiet", action="store_true", help="Hide progress messages.")
    return parser


@dataclass
class WeeklyResult:
    summary: FetchSummary
    report_count: int
    reading_list_report_path: Path
    weekly_report_path: Path


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


def rank_existing_reading_list(csv_path: Path, config_path: Path) -> int:
    papers = load_papers(csv_path)
    if not papers:
        return 0

    topics = load_topics(config_path) if config_path.exists() else {}
    ranked = rank_papers(papers, topics)
    write_papers(csv_path, ranked)
    return len(ranked)


def generate_report(csv_path: Path, output_path: Path) -> int:
    papers = load_papers(csv_path)
    write_markdown_report(papers, output_path)
    return len(papers)


def run_weekly(args: argparse.Namespace) -> WeeklyResult:
    progress = Progress(args.quiet)
    data_dir = Path(args.data_dir)
    reading_list_path = data_dir / "reading_list.csv"
    reading_list_report_path = data_dir / "reading_list.md"
    weekly_report_path = weekly_report_file(
        Path(args.weekly_reports_dir),
        args.report_date,
    )

    fetch_args = argparse.Namespace(
        topic=None,
        config_topic=None,
        fetch_all=True,
        max_results=args.max_results,
        new_results=not args.no_new_results,
        max_pages=args.max_pages,
        config=args.config,
        data_dir=args.data_dir,
        papers_dir=args.papers_dir,
        no_download=args.no_download,
        no_citations=args.no_citations,
        no_rank=False,
        quiet=args.quiet,
    )
    progress.log("Starting weekly workflow...")
    summary = run_fetch(fetch_args, argparse.ArgumentParser(prog="ai-paper-fetcher weekly"))
    progress.log("Generating reading list report...")
    report_count = generate_report(reading_list_path, reading_list_report_path)
    progress.log("Generating weekly report...")
    generate_report(reading_list_path, weekly_report_path)

    return WeeklyResult(
        summary=summary,
        report_count=report_count,
        reading_list_report_path=reading_list_report_path,
        weekly_report_path=weekly_report_path,
    )


def weekly_report_file(reports_dir: Path, report_date: str | None = None) -> Path:
    if report_date:
        try:
            parsed = date.fromisoformat(report_date)
        except ValueError as error:
            raise ValueError("--report-date must use YYYY-MM-DD format.") from error
    else:
        parsed = date.today()
    return reports_dir / f"{parsed.isoformat()}.md"


def run_fetch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> FetchSummary:
    data_dir = Path(args.data_dir)
    papers_dir = Path(args.papers_dir)
    progress = Progress(getattr(args, "quiet", False))

    if args.topic:
        return fetch(
            topic=args.topic,
            query=args.topic,
            max_results=args.max_results,
            data_dir=data_dir,
            papers_dir=papers_dir,
            no_download=args.no_download,
            enrich_with_citations=not args.no_citations,
            auto_rank=not args.no_rank,
            config_path=Path(args.config),
            new_results=args.new_results,
            max_pages=args.max_pages,
            progress=progress,
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
            auto_rank=not args.no_rank,
            config_path=Path(args.config),
            new_results=args.new_results,
            max_pages=args.max_pages,
            progress=progress,
        )

    if args.fetch_all:
        topics = load_topics(Path(args.config))
        summary = FetchSummary()
        for topic_config in topics.values():
            progress.log(f"Starting topic: {topic_config.name}")
            summary.add(
                fetch_config_topic(
                    topic_config,
                    max_results=args.max_results,
                    data_dir=data_dir,
                    papers_dir=papers_dir,
                    no_download=args.no_download,
                    enrich_with_citations=not args.no_citations,
                    auto_rank=False,
                    config_path=Path(args.config),
                    new_results=args.new_results,
                    max_pages=args.max_pages,
                    progress=progress,
                )
            )
        if not args.no_rank:
            progress.log("Ranking reading list...")
            summary.ranked = rank_existing_reading_list(data_dir / "reading_list.csv", Path(args.config))
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
    auto_rank: bool = True,
    config_path: Path | None = None,
    new_results: bool = False,
    max_pages: int = 5,
    progress: Progress | None = None,
) -> FetchSummary:
    return fetch(
        topic=topic_config.name,
        query=topic_config.query,
        max_results=max_results,
        data_dir=data_dir,
        papers_dir=papers_dir,
        no_download=no_download,
        enrich_with_citations=enrich_with_citations,
        auto_rank=auto_rank,
        config_path=config_path,
        new_results=new_results,
        max_pages=max_pages,
        progress=progress,
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
    auto_rank: bool = True,
    config_path: Path | None = None,
    new_results: bool = False,
    max_pages: int = 5,
    progress: Progress | None = None,
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
    categories: list[str] | None = None,
    published_after: str | None = None,
) -> FetchSummary:
    progress = progress or Progress()
    ensure_project_dirs(data_dir, papers_dir)
    reading_list_path = data_dir / "reading_list.csv"
    seen_path = data_dir / "seen_papers.json"

    seen = load_seen(seen_path)
    existing_ids = load_existing_ids(reading_list_path)
    known_ids = seen | existing_ids

    summary = FetchSummary()
    new_papers: list[Paper] = []

    page_size = max(1, max_results)
    page_limit = max(1, max_pages if new_results else 1)
    for page in range(page_limit):
        progress.log(f"Fetching {topic} page {page + 1}/{page_limit}...")
        papers = search_papers(
            query=query,
            max_results=page_size,
            start=page * page_size,
            topic=topic,
            categories=categories,
        )
        summary.pages_searched += 1
        if not papers:
            progress.log(f"No papers returned for {topic}; stopping.")
            break

        raw_count = len(papers)
        papers = filter_papers(
            papers,
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            published_after=published_after,
        )
        summary.found += len(papers)
        filtered_count = raw_count - len(papers)
        if filtered_count:
            progress.log(f"Filtered out {filtered_count} papers for {topic}.")

        for paper in papers:
            if paper.paper_id in known_ids:
                summary.skipped_duplicates += 1
                progress.log(f"Skipping duplicate: {paper.title}")
                continue

            if enrich_with_citations:
                progress.log(f"Looking up citations: {paper.title}")
                summary.citation_matches += enrich_citations([paper])

            if no_download:
                progress.log(f"Saving metadata: {paper.title}")
                new_papers.append(paper)
                known_ids.add(paper.paper_id)
                seen.add(paper.paper_id)
            else:
                try:
                    progress.log(f"Downloading PDF: {paper.title}")
                    path = download_pdf(paper, papers_dir)
                    mark_downloaded(paper, path)
                    summary.downloaded += 1
                except (OSError, URLError, ValueError) as error:
                    summary.failed_downloads += 1
                    paper.reason_to_read = f"PDF download failed: {error}"

                new_papers.append(paper)
                known_ids.add(paper.paper_id)
                seen.add(paper.paper_id)

            if new_results and len(new_papers) >= max_results:
                break

        progress.log(
            f"Topic {topic}: saved {len(new_papers)} new, skipped {summary.skipped_duplicates} duplicates so far."
        )
        if not new_results or len(new_papers) >= max_results:
            break

    append_papers(reading_list_path, new_papers)
    save_seen(seen_path, seen)
    summary.saved = len(new_papers)
    if auto_rank:
        progress.log("Ranking reading list...")
        summary.ranked = rank_existing_reading_list(reading_list_path, config_path or Path("config.yaml"))
    return summary


def print_summary(summary: FetchSummary, reading_list_path: Path) -> None:
    print(f"Found {summary.found} papers")
    print(f"Downloaded {summary.downloaded} new PDFs")
    print(f"Skipped {summary.skipped_duplicates} duplicates")
    if summary.failed_downloads:
        print(f"Failed to download {summary.failed_downloads} PDFs")
    print(f"Matched citation metadata for {summary.citation_matches} papers")
    if summary.ranked:
        print(f"Ranked {summary.ranked} papers")
    if summary.pages_searched > 1:
        print(f"Searched {summary.pages_searched} arXiv pages")
    print(f"Saved {summary.saved} metadata records to {reading_list_path.as_posix()}")
