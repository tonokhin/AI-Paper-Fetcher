import unittest

from ai_paper_fetcher.filtering import filter_papers
from ai_paper_fetcher.models import Paper


def paper(title: str, abstract: str, published_date: str = "2026-01-01") -> Paper:
    return Paper(
        paper_id=title,
        title=title,
        authors="",
        published_date=published_date,
        updated_date=published_date,
        abstract=abstract,
        categories="cs.CL",
        topic="test",
        pdf_url="",
    )


class FilteringTests(unittest.TestCase):
    def test_include_keywords(self):
        papers = [
            paper("Useful benchmark", "LLM evaluation"),
            paper("Unrelated", "Graph theory"),
        ]

        filtered = filter_papers(papers, include_keywords=["benchmark"])

        self.assertEqual([item.title for item in filtered], ["Useful benchmark"])

    def test_exclude_keywords(self):
        papers = [
            paper("Useful benchmark", "LLM evaluation"),
            paper("Survey paper", "LLM evaluation survey"),
        ]

        filtered = filter_papers(papers, exclude_keywords=["survey"])

        self.assertEqual([item.title for item in filtered], ["Useful benchmark"])

    def test_published_after(self):
        papers = [
            paper("Old", "LLM evaluation", "2025-12-31"),
            paper("New", "LLM evaluation", "2026-01-01"),
        ]

        filtered = filter_papers(papers, published_after="2026-01-01")

        self.assertEqual([item.title for item in filtered], ["New"])


if __name__ == "__main__":
    unittest.main()
