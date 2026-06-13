from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class TopicConfig:
    name: str
    query: str
    include_keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    published_after: str | None = None


def load_topics(config_path: Path) -> dict[str, TopicConfig]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    topics = raw.get("topics", {})
    if not isinstance(topics, dict):
        raise ValueError("Config must contain a 'topics' mapping.")

    return {
        name: _topic_from_mapping(name, value)
        for name, value in topics.items()
    }


def _topic_from_mapping(name: str, value: Any) -> TopicConfig:
    if not isinstance(value, dict):
        raise ValueError(f"Topic '{name}' must be a mapping.")

    query = value.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"Topic '{name}' must define a non-empty query.")

    return TopicConfig(
        name=name,
        query=query.strip(),
        include_keywords=_string_list(value.get("include_keywords", []), name, "include_keywords"),
        exclude_keywords=_string_list(value.get("exclude_keywords", []), name, "exclude_keywords"),
        categories=_string_list(value.get("categories", []), name, "categories"),
        published_after=_optional_string(value.get("published_after"), name, "published_after"),
    )


def _string_list(value: Any, topic: str, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Topic '{topic}' field '{field_name}' must be a list of strings.")
    return [item.strip() for item in value if item.strip()]


def _optional_string(value: Any, topic: str, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Topic '{topic}' field '{field_name}' must be a string.")
    return value.strip() or None
