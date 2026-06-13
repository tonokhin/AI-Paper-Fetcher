from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import FIELDNAMES, Paper


def ensure_project_dirs(data_dir: Path, papers_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    papers_dir.mkdir(parents=True, exist_ok=True)


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return set(str(item) for item in data)
    if isinstance(data, dict):
        return set(str(item) for item in data.get("paper_ids", []))
    return set()


def save_seen(path: Path, seen: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump({"paper_ids": sorted(seen)}, handle, indent=2)
        handle.write("\n")


def load_existing_ids(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["paper_id"] for row in reader if row.get("paper_id")}


def append_papers(csv_path: Path, papers: list[Paper]) -> None:
    if not papers:
        return

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    with csv_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for paper in papers:
            writer.writerow(paper.to_row())
