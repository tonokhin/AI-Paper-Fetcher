from __future__ import annotations

from .library import move_pdf_to_status_shelf, shelf_for_status
from .progress import load_progress, progress_path, save_progress, update_progress
from .storage import load_papers, write_papers
from .ui_state import UiState
from .ui_views import optional_int


def update_library_progress(state: UiState, form: dict[str, str]) -> None:
    paper_id = form.get("paper_id", "")
    if not paper_id:
        return

    csv_path = state.data_dir / "reading_list.csv"
    papers = load_papers(csv_path)
    progress_file = progress_path(state.data_dir)
    progress = load_progress(progress_file)

    status = form.get("status") or None
    understanding = optional_int(form.get("understanding"))
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
