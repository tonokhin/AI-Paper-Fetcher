from pathlib import Path
import tempfile
import unittest

from ai_paper_fetcher.models import FIELDNAMES, Paper
from ai_paper_fetcher.storage import append_papers, load_papers, write_papers


class StorageTests(unittest.TestCase):
    def test_append_papers_migrates_existing_csv_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "reading_list.csv"
            csv_path.write_text("paper_id,title\nold-id,Old title\n", encoding="utf-8")

            append_papers(
                csv_path,
                [
                    Paper(
                        paper_id="new-id",
                        title="New title",
                        authors="",
                        published_date="",
                        updated_date="",
                        abstract="",
                        categories="",
                        topic="",
                        pdf_url="",
                        citation_count="12",
                    )
                ],
            )

            header = csv_path.read_text(encoding="utf-8").splitlines()[0]

        self.assertEqual(header.split(","), FIELDNAMES)

    def test_write_and_load_papers(self):
        source = Paper(
            paper_id="paper-id",
            title="Paper title",
            authors="",
            published_date="",
            updated_date="",
            abstract="",
            categories="",
            topic="",
            pdf_url="",
            citation_count="12",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "reading_list.csv"

            write_papers(csv_path, [source])
            loaded = load_papers(csv_path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].paper_id, "paper-id")
        self.assertEqual(loaded[0].citation_count, "12")


if __name__ == "__main__":
    unittest.main()
