from datetime import date
import unittest

from ai_paper_fetcher.config import TopicConfig
from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.ranking import priority_for_score, rank_papers, score_paper


def paper(
    title: str,
    abstract: str,
    published_date: str = "2026-06-01",
    citation_count: str = "",
    topic: str = "llm_evaluation",
) -> Paper:
    return Paper(
        paper_id=title,
        title=title,
        authors="",
        published_date=published_date,
        updated_date=published_date,
        abstract=abstract,
        categories="cs.CL",
        topic=topic,
        pdf_url="",
        citation_count=citation_count,
    )


class RankingTests(unittest.TestCase):
    def test_priority_for_score(self):
        self.assertEqual(priority_for_score(10), "High")
        self.assertEqual(priority_for_score(5), "Medium")
        self.assertEqual(priority_for_score(4), "Low")

    def test_score_paper_uses_topic_keywords_high_value_terms_recency_and_citations(self):
        topic = TopicConfig(
            name="llm_evaluation",
            query="LLM evaluation",
            include_keywords=["benchmark"],
        )
        item = paper(
            title="A Benchmark for LLM Evaluation",
            abstract="This work studies reasoning.",
            published_date="2026-06-01",
            citation_count="25",
        )

        score = score_paper(item, topic, today=date(2026, 6, 13))

        self.assertGreaterEqual(score, 10)
        self.assertEqual(item.priority, "High")
        self.assertIn("benchmark", item.matched_keywords)
        self.assertIn("cited", item.matched_keywords)

    def test_score_paper_penalizes_excluded_keywords(self):
        topic = TopicConfig(
            name="llm_evaluation",
            query="LLM evaluation",
            include_keywords=[],
            exclude_keywords=["survey"],
        )
        item = paper("Survey of LLM Evaluation", "A survey.")

        score = score_paper(item, topic, today=date(2026, 6, 13))

        self.assertIn("excluded:survey", item.matched_keywords)
        self.assertLess(score, 10)

    def test_rank_papers_sorts_by_priority_then_score(self):
        low = paper("Unrelated", "Nothing special.", published_date="2025-01-01")
        high = paper("Benchmark for LLM Evaluation", "Reasoning evaluation.", citation_count="100")

        ranked = rank_papers(
            [low, high],
            {
                "llm_evaluation": TopicConfig(
                    name="llm_evaluation",
                    query="LLM evaluation",
                    include_keywords=["benchmark"],
                )
            },
            today=date(2026, 6, 13),
        )

        self.assertEqual(ranked[0].title, "Benchmark for LLM Evaluation")
        self.assertEqual(ranked[0].priority, "High")


if __name__ == "__main__":
    unittest.main()
