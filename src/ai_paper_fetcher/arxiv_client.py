from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .models import Paper
from .network import ssl_context
from .text import clean_whitespace


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def extract_arxiv_id(entry_id: str) -> str:
    raw_id = entry_id.rstrip("/").split("/")[-1]
    return raw_id.split("v")[0] if "v" in raw_id else raw_id


def search_papers(
    query: str,
    max_results: int = 10,
    start: int = 0,
    topic: str | None = None,
    categories: list[str] | None = None,
) -> list[Paper]:
    search_query = build_search_query(query, categories or [])
    params = urlencode(
        {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    url = f"{ARXIV_API_URL}?{params}"
    request = Request(url, headers={"User-Agent": "ai-paper-fetcher/0.1"})

    with urlopen(request, timeout=30, context=ssl_context()) as response:
        payload = response.read()

    return parse_arxiv_feed(payload, topic or query)


def fetch_paper_by_id(arxiv_id: str, topic: str) -> Paper | None:
    params = urlencode({"id_list": arxiv_id})
    url = f"{ARXIV_API_URL}?{params}"
    request = Request(url, headers={"User-Agent": "ai-paper-fetcher/0.1"})

    with urlopen(request, timeout=30, context=ssl_context()) as response:
        payload = response.read()

    papers = parse_arxiv_feed(payload, topic)
    return papers[0] if papers else None


def build_search_query(query: str, categories: list[str] | None = None) -> str:
    base_query = f'all:"{query}"'
    categories = categories or []
    if not categories:
        return base_query

    category_query = " OR ".join(f"cat:{category}" for category in categories)
    return f"{base_query} AND ({category_query})"


def parse_arxiv_feed(payload: bytes, topic: str) -> list[Paper]:
    root = ET.fromstring(payload)
    papers: list[Paper] = []

    for entry in root.findall(f"{ATOM}entry"):
        entry_id = _text(entry, f"{ATOM}id")
        title = clean_whitespace(_text(entry, f"{ATOM}title"))
        abstract = clean_whitespace(_text(entry, f"{ATOM}summary"))
        authors = ", ".join(
            clean_whitespace(_text(author, f"{ATOM}name"))
            for author in entry.findall(f"{ATOM}author")
        )
        categories = ", ".join(
            category.attrib.get("term", "")
            for category in entry.findall(f"{ATOM}category")
            if category.attrib.get("term")
        )
        pdf_url = _pdf_url(entry)
        doi = clean_whitespace(_text(entry, f"{ARXIV}doi"))

        papers.append(
            Paper(
                paper_id=extract_arxiv_id(entry_id),
                title=title,
                authors=authors,
                published_date=_date_only(_text(entry, f"{ATOM}published")),
                updated_date=_date_only(_text(entry, f"{ATOM}updated")),
                abstract=abstract,
                categories=categories,
                topic=topic,
                pdf_url=pdf_url,
                doi=doi,
            )
        )

    return papers


def _text(element: ET.Element, path: str) -> str:
    found = element.find(path)
    return found.text.strip() if found is not None and found.text else ""


def _pdf_url(entry: ET.Element) -> str:
    for link in entry.findall(f"{ATOM}link"):
        if link.attrib.get("title") == "pdf":
            return link.attrib.get("href", "")
    for link in entry.findall(f"{ATOM}link"):
        href = link.attrib.get("href", "")
        if "/pdf/" in href:
            return href
    return ""


def _date_only(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value[:10]
