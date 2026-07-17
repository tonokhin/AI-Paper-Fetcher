from __future__ import annotations

import shutil
from pathlib import Path

from .models import Paper
from .text import slugify


def shelf_for_status(status: str) -> str | None:
    if status == "skimmed":
        return "skimmed"
    if status == "understood":
        return "read"
    return None


def move_pdf_to_status_shelf(paper: Paper, papers_dir: Path, shelf: str) -> Path | None:
    if not paper.local_pdf_path:
        return None

    source = Path(paper.local_pdf_path)
    if not source.exists():
        return None

    status_dir = papers_dir / shelf / slugify(paper.topic)
    status_dir.mkdir(parents=True, exist_ok=True)

    if source.resolve().parent == status_dir.resolve():
        return source

    destination = unique_destination(status_dir / source.name)
    shutil.move(source.as_posix(), destination.as_posix())
    paper.local_pdf_path = destination.as_posix()
    return destination


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path

    for index in range(2, 10_000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate

    raise ValueError(f"Could not find an available destination for {path}")
