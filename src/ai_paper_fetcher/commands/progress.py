from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..library import move_pdf_to_status_shelf, shelf_for_status
from ..models import Paper
from ..progress import (
    LearningProgress,
    find_next_papers,
    format_progress,
    load_progress,
    progress_path,
    save_progress,
    update_progress,
)
from ..recommendations import Recommendation, recommend_next_papers
from ..storage import load_papers, write_papers
from ..tracks import filter_papers_by_track


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
        moved_pdf = None
        paper = papers_by_id.get(paper_id)
        shelf = shelf_for_status(item.status)
        if shelf is not None and paper is not None:
            moved_pdf = move_pdf_to_status_shelf(paper, Path(args.papers_dir), shelf)
            if moved_pdf is not None:
                write_papers(csv_path, papers)
        save_progress(progress_file, progress)
        print(f"Updated progress for {paper_id}")
        if moved_pdf is not None:
            print(f"Moved PDF to {moved_pdf.as_posix()}")
        print_progress_item(paper_id, item, papers_by_id.get(paper_id))
        return 0

    parser.error(f"Unknown progress action: {action}")
    return 2


def run_next(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    papers = load_papers(data_dir / "reading_list.csv")
    if args.track:
        try:
            papers = filter_papers_by_track(papers, Path(args.config), args.track)
        except ValueError as error:
            print(f"Track error: {error}", file=sys.stderr)
            return 1
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
