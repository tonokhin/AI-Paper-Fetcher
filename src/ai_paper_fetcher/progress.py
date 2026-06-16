from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import json
from pathlib import Path

from .models import Paper


STATUSES = ["queued", "skimmed", "reading", "understood", "archived"]


@dataclass
class LearningProgress:
    paper_id: str
    status: str = "queued"
    understanding: int = 0
    interest: str = ""
    last_touched: str = ""
    time_spent_minutes: int = 0
    notes: list[str] = field(default_factory=list)
    next_action: str = ""

    @classmethod
    def from_dict(cls, paper_id: str, data: dict[str, object]) -> "LearningProgress":
        notes = data.get("notes", [])
        return cls(
            paper_id=paper_id,
            status=str(data.get("status", "queued") or "queued"),
            understanding=_bounded_int(data.get("understanding", 0), 0, 5),
            interest=str(data.get("interest", "") or ""),
            last_touched=str(data.get("last_touched", "") or ""),
            time_spent_minutes=max(0, _bounded_int(data.get("time_spent_minutes", 0), 0, 1_000_000)),
            notes=[str(note) for note in notes] if isinstance(notes, list) else [],
            next_action=str(data.get("next_action", "") or ""),
        )

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data.pop("paper_id")
        return data


def progress_path(data_dir: Path) -> Path:
    return data_dir / "learning_progress.json"


def load_progress(path: Path) -> dict[str, LearningProgress]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        return {}

    papers = raw.get("papers", raw)
    if not isinstance(papers, dict):
        return {}

    progress: dict[str, LearningProgress] = {}
    for paper_id, item in papers.items():
        if isinstance(item, dict):
            progress[str(paper_id)] = LearningProgress.from_dict(str(paper_id), item)
    return progress


def save_progress(path: Path, progress: dict[str, LearningProgress]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "papers": {
            paper_id: item.to_dict()
            for paper_id, item in sorted(progress.items())
        }
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def update_progress(
    progress: dict[str, LearningProgress],
    paper_id: str,
    *,
    status: str | None = None,
    understanding: int | None = None,
    interest: str | None = None,
    time_spent_minutes: int | None = None,
    next_action: str | None = None,
    note: str | None = None,
) -> LearningProgress:
    item = progress.get(paper_id, LearningProgress(paper_id=paper_id))

    if status is not None:
        if status not in STATUSES:
            raise ValueError(f"status must be one of: {', '.join(STATUSES)}")
        item.status = status
    if understanding is not None:
        item.understanding = _bounded_int(understanding, 0, 5)
    if interest is not None:
        item.interest = interest
    if time_spent_minutes is not None:
        item.time_spent_minutes = max(0, item.time_spent_minutes + time_spent_minutes)
    if next_action is not None:
        item.next_action = next_action
    if note:
        item.notes.append(note)

    item.last_touched = date.today().isoformat()
    progress[paper_id] = item
    return item


def find_next_papers(
    papers: list[Paper],
    progress: dict[str, LearningProgress],
    limit: int = 5,
) -> list[Paper]:
    candidates = [
        paper
        for paper in papers
        if progress.get(paper.paper_id, LearningProgress(paper.paper_id)).status not in {"understood", "archived"}
    ]
    return candidates[: max(1, limit)]


def format_progress(item: LearningProgress) -> list[str]:
    lines = [
        f"Status: {item.status}",
        f"Understanding: {item.understanding}/5",
    ]
    if item.interest:
        lines.append(f"Interest: {item.interest}")
    if item.time_spent_minutes:
        lines.append(f"Time spent: {item.time_spent_minutes} minutes")
    if item.last_touched:
        lines.append(f"Last touched: {item.last_touched}")
    if item.next_action:
        lines.append(f"Next action: {item.next_action}")
    if item.notes:
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in item.notes)
    return lines


def _bounded_int(value: object, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = minimum
    return min(max(parsed, minimum), maximum)
