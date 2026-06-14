from pathlib import Path
from io import StringIO
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


def sample_paper_with_id(paper_id: str) -> Paper:
    item = sample_paper()
    item.paper_id = paper_id
    item.title = f"A Benchmark for LLM Evaluation {paper_id}"
    return item


def write_one_topic_config(path: Path) -> None:
    path.write_text(
        """
topics:
  llm_evaluation:
    query: "LLM evaluation"
    include_keywords:
      - benchmark
    exclude_keywords: []
    categories:
      - cs.CL
""",
        encoding="utf-8",
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

    def test_fetch_new_results_keeps_paging_past_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            write_papers(data_dir / "reading_list.csv", [sample_paper_with_id("duplicate")])

            pages = [
                [sample_paper_with_id("duplicate")],
                [sample_paper_with_id("new-1")],
                [sample_paper_with_id("new-2")],
            ]
            with patch("ai_paper_fetcher.cli.search_papers", side_effect=pages) as search:
                exit_code = main(
                    [
                        "fetch",
                        "--topic",
                        "llm_evaluation",
                        "--max-results",
                        "2",
                        "--new-results",
                        "--max-pages",
                        "3",
                        "--no-download",
                        "--no-citations",
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(search.call_count, 3)
        self.assertEqual({paper.paper_id for paper in papers}, {"duplicate", "new-1", "new-2"})

    def test_fetch_without_new_results_stops_after_first_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            write_papers(data_dir / "reading_list.csv", [sample_paper_with_id("duplicate")])

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper_with_id("duplicate")]) as search:
                exit_code = main(
                    [
                        "fetch",
                        "--topic",
                        "llm_evaluation",
                        "--max-results",
                        "2",
                        "--no-download",
                        "--no-citations",
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(search.call_count, 1)
        self.assertEqual([paper.paper_id for paper in papers], ["duplicate"])

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
            config_path = Path(temp_dir) / "config.yaml"
            write_one_topic_config(config_path)

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper()]):
                exit_code = main(
                    [
                        "weekly",
                        "--max-results",
                        "1",
                        "--no-download",
                        "--no-citations",
                        "--config",
                        str(config_path),
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

    def test_weekly_uses_new_results_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            config_path = Path(temp_dir) / "config.yaml"
            write_one_topic_config(config_path)
            write_papers(data_dir / "reading_list.csv", [sample_paper_with_id("duplicate")])

            pages = [
                [sample_paper_with_id("duplicate")],
                [sample_paper_with_id("new-1")],
            ]
            with patch("ai_paper_fetcher.cli.search_papers", side_effect=pages) as search:
                exit_code = main(
                    [
                        "weekly",
                        "--max-results",
                        "1",
                        "--max-pages",
                        "2",
                        "--no-download",
                        "--no-citations",
                        "--config",
                        str(config_path),
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                        "--weekly-reports-dir",
                        str(Path(temp_dir) / "weekly_reports"),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(search.call_count, 2)
        self.assertEqual({paper.paper_id for paper in papers}, {"duplicate", "new-1"})

    def test_weekly_can_disable_new_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            config_path = Path(temp_dir) / "config.yaml"
            write_one_topic_config(config_path)
            write_papers(data_dir / "reading_list.csv", [sample_paper_with_id("duplicate")])

            with patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper_with_id("duplicate")]) as search:
                exit_code = main(
                    [
                        "weekly",
                        "--max-results",
                        "1",
                        "--no-new-results",
                        "--no-download",
                        "--no-citations",
                        "--config",
                        str(config_path),
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                        "--weekly-reports-dir",
                        str(Path(temp_dir) / "weekly_reports"),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(search.call_count, 1)
        self.assertEqual([paper.paper_id for paper in papers], ["duplicate"])

    def test_weekly_fast_mode_uses_lightweight_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            papers_dir = Path(temp_dir) / "papers"
            config_path = Path(temp_dir) / "config.yaml"
            write_one_topic_config(config_path)

            pages = [
                [sample_paper_with_id("new-1")],
                [sample_paper_with_id("new-2")],
            ]
            with (
                patch("ai_paper_fetcher.cli.search_papers", side_effect=pages) as search,
                patch("ai_paper_fetcher.cli.enrich_citations") as citations,
            ):
                exit_code = main(
                    [
                        "weekly",
                        "--fast",
                        "--max-results",
                        "20",
                        "--max-pages",
                        "10",
                        "--config",
                        str(config_path),
                        "--data-dir",
                        str(data_dir),
                        "--papers-dir",
                        str(papers_dir),
                        "--weekly-reports-dir",
                        str(Path(temp_dir) / "weekly_reports"),
                    ]
                )

            papers = load_papers(data_dir / "reading_list.csv")

        self.assertEqual(exit_code, 0)
        self.assertEqual(search.call_count, 2)
        self.assertEqual(search.call_args_list[0].kwargs["max_results"], 3)
        self.assertEqual(len(papers), 2)
        citations.assert_not_called()
        self.assertEqual(list(papers_dir.glob("**/*.pdf")), [])

    def test_quiet_hides_progress_messages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"

            with (
                patch("ai_paper_fetcher.cli.search_papers", return_value=[sample_paper()]),
                patch("sys.stderr", new_callable=StringIO) as stderr,
            ):
                exit_code = main(
                    [
                        "fetch",
                        "--topic",
                        "llm_evaluation",
                        "--no-download",
                        "--no-citations",
                        "--quiet",
                        "--data-dir",
                        str(data_dir),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
