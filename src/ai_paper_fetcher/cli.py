from __future__ import annotations

import argparse
import sys
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError

from .arxiv_client import fetch_paper_by_id, search_papers
from .citations import enrich_citations
from .config import FoundationalPaperConfig, TopicConfig, load_foundational_papers, load_topics
from .downloader import download_pdf, mark_downloaded
from .filtering import filter_papers
from .models import Paper
from .progress import (
    STATUSES,
    LearningProgress,
    find_next_papers,
    format_progress,
    load_progress,
    progress_path,
    save_progress,
    update_progress,
)
from .ranking import rank_papers
from .recommendations import Recommendation, recommend_next_papers
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
    updated: int = 0

    def add(self, other: "FetchSummary") -> None:
        self.found += other.found
        self.downloaded += other.downloaded
        self.skipped_duplicates += other.skipped_duplicates
        self.failed_downloads += other.failed_downloads
        self.citation_matches += other.citation_matches
        self.saved += other.saved
        self.ranked += other.ranked
        self.pages_searched += other.pages_searched
        self.updated += other.updated


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "progress":
        try:
            return run_progress(args, parser)
        except ValueError as error:
            print(f"Progress error: {error}", file=sys.stderr)
            return 1

    if args.command == "next":
        return run_next(args)

    if args.command == "download-missing":
        summary = download_missing_pdfs(
            Path(args.data_dir) / "reading_list.csv",
            Path(args.papers_dir),
            Progress(args.quiet),
        )
        print_summary(summary, Path(args.data_dir) / "reading_list.csv")
        return 0

    if args.command == "foundations":
        try:
            summary = run_foundations(args)
        except (FileNotFoundError, ValueError) as error:
            print(f"Foundations error: {error}", file=sys.stderr)
            return 1
        except URLError as error:
            print(f"Could not reach arXiv or OpenAlex: {error}", file=sys.stderr)
            return 1

        print_summary(summary, Path(args.data_dir) / "reading_list.csv")
        return 0

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
        count = generate_report(Path(args.data_dir) / "reading_list.csv", output_path, progress_path(Path(args.data_dir)))
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
        choices=["fetch", "citations", "rank", "report", "weekly", "foundations", "download-missing", "progress", "next"],
        help="Command to run.",
    )
    parser.add_argument(
        "progress_action",
        nargs="?",
        choices=["list", "next", "show", "update", "note"],
        help="Progress action to run when command is progress.",
    )
    parser.add_argument("progress_paper_id", nargs="?", help="Paper ID for progress show, update, or note.")
    parser.add_argument("progress_text", nargs="*", help="Note text for progress note.")
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
    parser.add_argument(
        "--foundations-config",
        default="foundational_papers.yaml",
        help="Path to foundational papers YAML.",
    )
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
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Quick weekly mode: max-results 3, max-pages 2, no PDF downloads, no citation lookups.",
    )
    parser.add_argument("--quiet", action="store_true", help="Hide progress messages.")
    parser.add_argument("--status", choices=STATUSES, help="Learning status for progress update.")
    parser.add_argument("--understanding", type=int, help="Understanding level from 0 to 5.")
    parser.add_argument("--interest", help="Personal interest label, such as high, medium, or low.")
    parser.add_argument("--minutes", type=int, help="Minutes to add to this paper's time spent.")
    parser.add_argument("--next-action", help="Next learning action for this paper.")
    parser.add_argument("--limit", type=int, help="Maximum items for progress list or next.")
    return parser


@dataclass
class WeeklyResult:
    summary: FetchSummary
    report_count: int
    reading_list_report_path: Path
    weekly_report_path: Path


def run_foundations(args: argparse.Namespace) -> FetchSummary:
    progress = Progress(args.quiet)
    data_dir = Path(args.data_dir)
    papers_dir = Path(args.papers_dir)
    ensure_project_dirs(data_dir, papers_dir)

    reading_list_path = data_dir / "reading_list.csv"
    seen_path = data_dir / "seen_papers.json"
    seen = load_seen(seen_path)
    known_ids = seen | load_existing_ids(reading_list_path)
    foundation_configs = load_foundational_papers(Path(args.foundations_config))
    summary = FetchSummary()
    new_papers: list[Paper] = []

    for foundation in foundation_configs:
        progress.log(f"Fetching foundational paper: {foundation.title}")
        paper = fetch_foundational_paper(foundation)
        summary.found += 1

        if paper is None:
            summary.failed_downloads += 1
            progress.log(f"Could not find arXiv metadata for {foundation.arxiv_id}")
            continue

        if paper.paper_id in known_ids:
            summary.skipped_duplicates += 1
            progress.log(f"Skipping duplicate: {paper.title}")
            continue

        if not args.no_citations:
            progress.log(f"Looking up citations: {paper.title}")
            summary.citation_matches += enrich_citations([paper])

        if args.no_download:
            progress.log(f"Saving metadata: {paper.title}")
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

    append_papers(reading_list_path, new_papers)
    save_seen(seen_path, seen)
    summary.saved = len(new_papers)
    if not args.no_rank:
        progress.log("Ranking reading list...")
        summary.ranked = rank_existing_reading_list(reading_list_path, Path(args.config))
    return summary


def download_missing_pdfs(csv_path: Path, papers_dir: Path, progress: Progress | None = None) -> FetchSummary:
    progress = progress or Progress()
    papers = load_papers(csv_path)
    summary = FetchSummary(found=len(papers))
    changed = False

    for paper in papers:
        if not paper_needs_pdf(paper):
            continue

        try:
            progress.log(f"Downloading missing PDF: {paper.title}")
            path = download_pdf(paper, papers_dir)
            mark_downloaded(paper, path)
            summary.downloaded += 1
            summary.updated += 1
            changed = True
        except (OSError, URLError, ValueError) as error:
            summary.failed_downloads += 1
            paper.reason_to_read = f"PDF download failed: {error}"
            changed = True

    if changed:
        write_papers(csv_path, papers)

    return summary


def paper_needs_pdf(paper: Paper) -> bool:
    if not paper.pdf_url:
        return False
    if not paper.local_pdf_path:
        return True
    return not Path(paper.local_pdf_path).exists()


def fetch_foundational_paper(config: FoundationalPaperConfig) -> Paper | None:
    paper = fetch_paper_by_id(config.arxiv_id, config.topic)
    if paper is None:
        return None
    paper.collection = "foundational"
    if config.note:
        paper.reason_to_read = f"Foundational paper: {config.note}"
    return paper


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


def generate_report(csv_path: Path, output_path: Path, progress_file: Path | None = None) -> int:
    papers = load_papers(csv_path)
    progress = load_progress(progress_file) if progress_file else {}
    write_markdown_report(papers, output_path, progress)
    return len(papers)


def run_progress(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    action = args.progress_action
    if not action:
        parser.error("progress requires one of: list, next, show, update, note")

    data_dir = Path(args.data_dir)
    csv_path = data_dir / "reading_list.csv"
    progress_file = progress_path(data_dir)
    progress = load_progress(progress_file)

    if action == "list":
        print_progress_list(progress, limit=args.limit or 5)
        return 0

    papers = load_papers(csv_path)
    papers_by_id = {paper.paper_id: paper for paper in papers}

    if action == "next":
        print_next_papers(papers, progress, limit=args.limit or 5)
        return 0

    paper_id = args.progress_paper_id
    if not paper_id:
        parser.error(f"progress {action} requires a paper ID")

    if action == "show":
        print_progress_item(paper_id, progress.get(paper_id), papers_by_id.get(paper_id))
        return 0

    if action == "note":
        note = " ".join(args.progress_text).strip()
        if not note:
            parser.error("progress note requires note text")
        item = update_progress(progress, paper_id, note=note)
        save_progress(progress_file, progress)
        print(f"Added note for {paper_id}")
        print_progress_item(paper_id, item, papers_by_id.get(paper_id))
        return 0

    if action == "update":
        item = update_progress(
            progress,
            paper_id,
            status=args.status,
            understanding=args.understanding,
            interest=args.interest,
            time_spent_minutes=args.minutes,
            next_action=args.next_action,
        )
        save_progress(progress_file, progress)
        print(f"Updated progress for {paper_id}")
        print_progress_item(paper_id, item, papers_by_id.get(paper_id))
        return 0

    parser.error(f"Unknown progress action: {action}")
    return 2


def run_next(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    papers = load_papers(data_dir / "reading_list.csv")
    progress = load_progress(progress_path(data_dir))
    recommendations = recommend_next_papers(papers, progress, limit=args.limit or 1)

    if not recommendations:
        print("No unread papers found.")
        return 0

    for index, recommendation in enumerate(recommendations, start=1):
        print_next_recommendation(recommendation, index=index, show_rank=len(recommendations) > 1)
    return 0


def print_next_recommendation(
    recommendation: Recommendation,
    *,
    index: int = 1,
    show_rank: bool = False,
) -> None:
    paper = recommendation.paper
    prefix = f"{index}. " if show_rank else ""
    print(f"{prefix}{paper.paper_id}: {paper.title}")
    print(f"  Recommendation score: {recommendation.score:.1f}")
    if recommendation.progress:
        print(f"  Progress: {recommendation.progress.status}, understanding {recommendation.progress.understanding}/5")
    else:
        print("  Progress: not started")
    if paper.citation_count:
        print(f"  Citation graph signal: {paper.citation_count} citations")
    elif paper.openalex_id:
        print("  Citation graph signal: OpenAlex metadata available")
    else:
        print("  Citation graph signal: no citation metadata yet")
    if paper.local_pdf_path:
        print(f"  PDF: {paper.local_pdf_path}")
    print(f"  Why: {'; '.join(recommendation.reasons)}")


def print_progress_list(progress: dict[str, LearningProgress], limit: int = 5) -> None:
    active = [
        item
        for item in progress.values()
        if item.status not in {"understood", "archived"}
    ]
    active.sort(key=lambda item: (item.status != "reading", item.last_touched), reverse=False)
    if not active:
        print("No active learning progress yet.")
        return
    for item in active[: max(1, limit)]:
        print(f"{item.paper_id}: {item.status}, understanding {item.understanding}/5")
        if item.next_action:
            print(f"  Next: {item.next_action}")


def print_next_papers(
    papers: list[Paper],
    progress: dict[str, LearningProgress],
    limit: int = 5,
) -> None:
    next_papers = find_next_papers(papers, progress, limit)
    if not next_papers:
        print("No unread papers found.")
        return
    for paper in next_papers:
        item = progress.get(paper.paper_id)
        status = item.status if item else "queued"
        understanding = item.understanding if item else 0
        print(f"{paper.paper_id}: {paper.title}")
        print(f"  Status: {status}; understanding {understanding}/5")
        if paper.local_pdf_path:
            print(f"  PDF: {paper.local_pdf_path}")


def print_progress_item(
    paper_id: str,
    item: LearningProgress | None,
    paper: Paper | None = None,
) -> None:
    if paper:
        print(paper.title)
    print(f"Paper ID: {paper_id}")
    if not item:
        print("No progress recorded.")
        return
    for line in format_progress(item):
        print(line)


def run_weekly(args: argparse.Namespace) -> WeeklyResult:
    apply_fast_mode(args)
    progress = Progress(args.quiet)
    data_dir = Path(args.data_dir)
    reading_list_path = data_dir / "reading_list.csv"
    reading_list_report_path = data_dir / "reading_list.md"
    learning_progress_path = progress_path(data_dir)
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
    report_count = generate_report(reading_list_path, reading_list_report_path, learning_progress_path)
    progress.log("Generating weekly report...")
    generate_report(reading_list_path, weekly_report_path, learning_progress_path)

    return WeeklyResult(
        summary=summary,
        report_count=report_count,
        reading_list_report_path=reading_list_report_path,
        weekly_report_path=weekly_report_path,
    )


def apply_fast_mode(args: argparse.Namespace) -> None:
    if not args.fast:
        return
    args.max_results = 3
    args.max_pages = 2
    args.no_download = True
    args.no_citations = True


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
    if summary.updated:
        print(f"Updated {summary.updated} existing metadata records")
    print(f"Saved {summary.saved} metadata records to {reading_list_path.as_posix()}")
