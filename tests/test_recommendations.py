import unittest

from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.progress import LearningProgress
from ai_paper_fetcher.recommendations import recommend_next_papers


def paper(
    paper_id: str,
    title: str,
    relevance_score: str = "",
    citation_count: str = "",
    collection: str = "",
) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        authors="",
        published_date="",
        updated_date="",
        abstract="",
        categories="",
        topic="",
        pdf_url="",
        relevance_score=relevance_score,
        citation_count=citation_count,
        collection=collection,
        local_pdf_path=f"papers/{paper_id}.pdf",
    )


class RecommendationTests(unittest.TestCase):
    def test_recommend_next_papers_uses_progress_and_citations(self):
        finished = paper("done", "Finished paper", relevance_score="100", citation_count="1000")
        cited = paper("cited", "Cited paper", relevance_score="12", citation_count="100")
        reading = paper("reading", "Current paper", relevance_score="10", citation_count="5")
        progress = {
            "done": LearningProgress(paper_id="done", status="understood"),
            "reading": LearningProgress(paper_id="reading", status="reading", understanding=2),
        }

        recommendations = recommend_next_papers([finished, cited, reading], progress, limit=2)

        self.assertNotIn("done", [item.paper.paper_id for item in recommendations])
        self.assertEqual(recommendations[0].paper.paper_id, "reading")
        self.assertIn("currently reading", "; ".join(recommendations[0].reasons))
        self.assertIn("100 citations", "; ".join(recommendations[1].reasons))


if __name__ == "__main__":
    unittest.main()
