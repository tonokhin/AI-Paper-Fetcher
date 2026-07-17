import tempfile
import unittest
from pathlib import Path

from ai_paper_fetcher.library import move_pdf_to_status_shelf, shelf_for_status
from ai_paper_fetcher.models import Paper


def paper(local_pdf_path: str = "") -> Paper:
    return Paper(
        paper_id="paper-1",
        title="A Benchmark for LLM Evaluation",
        authors="Ada Lovelace",
        published_date="2026-01-01",
        updated_date="2026-01-02",
        abstract="A benchmark paper.",
        categories="cs.CL",
        topic="llm_evaluation",
        pdf_url="https://arxiv.org/pdf/2601.00001",
        local_pdf_path=local_pdf_path,
    )


class LibraryTest(unittest.TestCase):
    def test_shelf_for_status_maps_progress_statuses_to_pdf_shelves(self):
        self.assertEqual(shelf_for_status("skimmed"), "skimmed")
        self.assertEqual(shelf_for_status("understood"), "read")
        self.assertIsNone(shelf_for_status("reading"))

    def test_move_pdf_to_status_shelf_moves_pdf_and_updates_paper(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            papers_dir = Path(temp_dir) / "papers"
            source = papers_dir / "llm_evaluation" / "paper.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("pdf", encoding="utf-8")
            item = paper(source.as_posix())

            destination = move_pdf_to_status_shelf(item, papers_dir, "skimmed")

            expected = papers_dir / "skimmed" / "llm_evaluation" / "paper.pdf"
            self.assertEqual(destination, expected)
            self.assertEqual(item.local_pdf_path, expected.as_posix())
            self.assertTrue(expected.exists())
            self.assertFalse(source.exists())

    def test_move_pdf_to_status_shelf_uses_unique_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            papers_dir = Path(temp_dir) / "papers"
            source = papers_dir / "llm_evaluation" / "paper.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("pdf", encoding="utf-8")
            existing = papers_dir / "read" / "llm_evaluation" / "paper.pdf"
            existing.parent.mkdir(parents=True)
            existing.write_text("existing", encoding="utf-8")
            item = paper(source.as_posix())

            destination = move_pdf_to_status_shelf(item, papers_dir, "read")

            expected = papers_dir / "read" / "llm_evaluation" / "paper-2.pdf"
            self.assertEqual(destination, expected)
            self.assertEqual(item.local_pdf_path, expected.as_posix())
            self.assertTrue(expected.exists())
            self.assertTrue(existing.exists())


if __name__ == "__main__":
    unittest.main()
