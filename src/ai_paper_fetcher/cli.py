from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.error import URLError

from .commands.progress import run_next, run_progress
from .curriculum_export import export_curriculum_resources
from .progress import STATUSES, progress_path
from .ui import run_ui
from .workflows import (
    Progress,
    download_missing_pdfs,
    enrich_existing_reading_list,
    generate_report,
    print_summary,
    rank_existing_reading_list,
    run_fetch,
    run_foundations,
    run_weekly,
    weekly_report_file,
)


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

    if args.command == "ui":
        run_ui(
            data_dir=Path(args.data_dir),
            papers_dir=Path(args.papers_dir),
            config_path=Path(args.config),
            host=args.host,
            port=args.port,
        )
        return 0

    if args.command == "download-missing":
        summary = download_missing_pdfs(
            Path(args.data_dir) / "reading_list.csv",
            Path(args.papers_dir),
            Progress(args.quiet),
        )
        print_summary(summary, Path(args.data_dir) / "reading_list.csv")
        return 0

    if args.command == "export-curriculum-resources":
        try:
            result = export_curriculum_resources(
                reading_list_path=Path(args.data_dir) / "reading_list.csv",
                mapping_path=Path(args.mapping),
                output_path=Path(args.out),
                estimated_hours=args.estimated_hours,
                skip_unmapped=args.skip_unmapped,
            )
        except (FileNotFoundError, ValueError) as error:
            print(f"Curriculum export error: {error}", file=sys.stderr)
            return 1

        print(f"Exported {result.written} curriculum resources to {Path(args.out).as_posix()}")
        if result.skipped_unmapped:
            print(f"Skipped unmapped topics: {', '.join(result.skipped_unmapped)}")
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
        choices=[
            "fetch",
            "citations",
            "rank",
            "report",
            "weekly",
            "foundations",
            "download-missing",
            "export-curriculum-resources",
            "progress",
            "next",
            "ui",
        ],
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
    parser.add_argument("--track", help="Named track from config.yaml to limit fetch, weekly, or next.")
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
        "--mapping",
        default="curriculum_mapping.yaml",
        help="Path to curriculum topic mapping YAML.",
    )
    parser.add_argument(
        "--out",
        default="resources/generated-ai-papers.yaml",
        help="Output path for exported curriculum resource YAML.",
    )
    parser.add_argument(
        "--estimated-hours",
        type=float,
        default=6.0,
        help="Estimated study hours assigned to each exported paper resource.",
    )
    parser.add_argument(
        "--skip-unmapped",
        action="store_true",
        help="Skip papers whose topic is not present in the curriculum mapping.",
    )
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
    parser.add_argument("--host", default="127.0.0.1", help="Host for the local UI server.")
    parser.add_argument("--port", type=int, default=8765, help="Port for the local UI server.")
    return parser
