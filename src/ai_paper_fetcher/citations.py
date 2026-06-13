from __future__ import annotations

import json
import os
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .models import Paper
from .network import ssl_context


OPENALEX_API_URL = "https://api.openalex.org/works"


@dataclass
class CitationMetadata:
    citation_count: int
    source: str
    openalex_id: str = ""


def enrich_citations(papers: list[Paper]) -> int:
    enriched = 0
    for paper in papers:
        try:
            metadata = lookup_citation_metadata(paper)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            continue

        if metadata is None:
            continue

        paper.citation_count = str(metadata.citation_count)
        paper.citation_source = metadata.source
        paper.openalex_id = metadata.openalex_id
        enriched += 1

    return enriched


def lookup_citation_metadata(paper: Paper) -> CitationMetadata | None:
    if paper.doi:
        metadata = lookup_by_doi(paper.doi)
        if metadata is not None:
            return metadata

    return lookup_by_title(paper.title)


def lookup_by_doi(doi: str) -> CitationMetadata | None:
    url = f"{OPENALEX_API_URL}/doi:{quote(doi, safe='')}"
    try:
        payload = _get_json(url)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise

    return _metadata_from_work(payload, "OpenAlex DOI")


def lookup_by_title(title: str) -> CitationMetadata | None:
    if not title:
        return None

    params = urlencode(
        {
            "search": title,
            "per-page": 1,
            "select": "id,title,cited_by_count",
        }
    )
    payload = _get_json(f"{OPENALEX_API_URL}?{params}")
    results = payload.get("results", [])
    if not results:
        return None

    result = results[0]
    result_title = result.get("title") or ""
    if _title_similarity(title, result_title) < 0.82:
        return None

    return _metadata_from_work(result, "OpenAlex title")


def _get_json(url: str) -> dict:
    request = Request(url, headers=_headers())
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def _headers() -> dict[str, str]:
    headers = {"User-Agent": "ai-paper-fetcher/0.1"}
    api_key = os.environ.get("OPENALEX_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _metadata_from_work(work: dict, source: str) -> CitationMetadata:
    return CitationMetadata(
        citation_count=int(work.get("cited_by_count") or 0),
        source=source,
        openalex_id=str(work.get("id") or ""),
    )


def _title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalize_title(left), _normalize_title(right)).ratio()


def _normalize_title(value: str) -> str:
    return " ".join(value.lower().split())
