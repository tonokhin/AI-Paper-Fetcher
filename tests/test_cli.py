from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ai_paper_fetcher.cli import main
from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.storage import load_papers


def sample_paper() -> Paper:
    return Paper(
        paper_id="paper-1",
        title="A Benchmark for LLM Evaluation",
        authors="",
        published_date="2026-06-01",
        updated_date="2026-06-01",
        abstract="This paper studies reasoning.",
        categories="cs.CL",
        topic="llm_evaluation",
        pdf_url="",
    )


class CliTests(unittest.TestCase):
    def test_fetch_ranks_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper()]):
                exit_code = main(
                    [
                        "fetch",
                        "--topic",
                        "llm_evaluation",
                        "--no-download",
                        "--no-citations",
                        "--data-dir",
                        str(data_dir),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(papers[0].priority, "High")
        self.assertTrue(papers[0].relevance_score)

    def test_fetch_can_skip_ranking(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper()]):
                exit_code = main(
                    [
                        "fetch",
                        "--topic",
                        "llm_evaluation",
                        "--no-download",
                        "--no-citations",
                        "--no-rank",
                        "--data-dir",
                        str(data_dir),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(papers[0].priority, "")
        self.assertEqual(papers[0].relevance_score, "")


if __name__ == "__main__":
    unittest.main()
