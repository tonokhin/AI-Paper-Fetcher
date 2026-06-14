from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ai_paper_fetcher.cli import main, weekly_report_file
from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.storage import load_papers, write_papers


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

    def test_report_command_writes_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            data_dir.mkdir()
            write_papers(data_dir / "reading_list.csv", [sample_paper()])

            exit_code = main(["report", "--data-dir", str(data_dir)])

            report = (data_dir / "reading_list.md").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("# AI Paper Reading List", report)
        self.assertIn("A Benchmark for LLM Evaluation", report)

    def test_weekly_report_file_uses_date(self):
        path = weekly_report_file(Path("weekly_reports"), "2026-06-14")

        self.assertEqual(path, Path("weekly_reports") / "2026-06-14.md")

    def test_weekly_command_fetches_and_writes_reports(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            weekly_dir = Path(temp_dir) / "weekly_reports"

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper()]):
                exit_code = main(
                    [
                        "weekly",
                        "--max-results",
                        "1",
                        "--no-download",
                        "--no-citations",
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                        "--weekly-reports-dir",
                        str(weekly_dir),
                        "--report-date",
                        "2026-06-14",
                    ]
                )

            reading_list_report = data_dir / "reading_list.md"
            weekly_report = weekly_dir / "2026-06-14.md"

            self.assertEqual(exit_code, 0)
            self.assertTrue(reading_list_report.exists())
            self.assertTrue(weekly_report.exists())


if __name__ == "__main__":
    unittest.main()
