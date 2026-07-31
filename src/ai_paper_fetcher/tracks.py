from __future__ import annotations

from pathlib import Path

from .config import load_topics, load_tracks
from .models import Paper


def filter_papers_by_track(papers: list[Paper], config_path: Path, track_name: str) -> list[Paper]:
    topic_names = set(topic_names_for_track(config_path, track_name))
    return [paper for paper in papers if paper.topic in topic_names]


def topic_names_for_track(config_path: Path, track_name: str) -> list[str]:
    tracks = load_tracks(config_path)
    if track_name not in tracks:
        raise ValueError(f"Unknown track: {track_name}")

    topics = load_topics(config_path)
    missing = [topic for topic in tracks[track_name].topics if topic not in topics]
    if missing:
        raise ValueError(f"Track '{track_name}' references unknown topics: {', '.join(missing)}")
    return tracks[track_name].topics
