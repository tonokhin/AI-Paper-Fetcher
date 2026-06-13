from dataclasses import asdict, dataclass


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: str
    published_date: str
    updated_date: str
    abstract: str
    categories: str
    topic: str
    pdf_url: str
    local_pdf_path: str = ""
    relevance_score: str = ""
    matched_keywords: str = ""
    priority: str = ""
    reason_to_read: str = ""
    downloaded_at: str = ""

    def to_row(self) -> dict[str, str]:
        return asdict(self)


FIELDNAMES = [
    "paper_id",
    "title",
    "authors",
    "published_date",
    "updated_date",
    "abstract",
    "categories",
    "topic",
    "pdf_url",
    "local_pdf_path",
    "relevance_score",
    "matched_keywords",
    "priority",
    "reason_to_read",
    "downloaded_at",
]
