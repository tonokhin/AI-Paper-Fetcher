from pathlib import Path
import tempfile
import unittest

from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.reporting import render_markdown_report, write_markdown_report


def paper() -> Paper:
    return Paper(
        paper_id="paper-1",
        title="A Benchmark for LLM Evaluation",
        authors="Ada Lovelace",
        published_date="2026-06-01",
        updated_date="2026-06-01",
        abstract="This paper introduces a benchmark for evaluating reasoning models.",
        categories="cs.CL",
        topic="llm_evaluation",
        pdf_url="https://arxiv.org/pdf/1234.5678",
        citation_count="12",
        openalex_id="https://openalex.org/W1",
        local_pdf_path="papers/llm_evaluation/paper.pdf",
        relevance_score="18",
        matched_keywords="benchmark, evaluation",
        priority="High",
        reason_to_read="Matches benchmark and evaluation.",
    )


class ReportingTests(unittest.TestCase):
    def test_render_markdown_report_groups_by_priority_and_topic(self):
        markdown = render_markdown_report([paper()])

        self.assertIn("# AI Paper Reading List", markdown)
        self.assertIn("## High Priority", markdown)
        self.assertIn("### LLM Evaluation", markdown)
        self.assertIn("#### A Benchmark for LLM Evaluation", markdown)
        self.assertIn("- Score: 18", markdown)
        self.assertIn("- Citations: 12", markdown)
        self.assertIn("- Local PDF: papers/llm_evaluation/paper.pdf", markdown)
        self.assertIn("- OpenAlex: https://openalex.org/W1", markdown)

    def test_write_markdown_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "reading_list.md"

            write_markdown_report([paper()], output_path)

            content = output_path.read_text(encoding="utf-8")

        self.assertIn("A Benchmark for LLM Evaluation", content)


if __name__ == "__main__":
    unittest.main()
