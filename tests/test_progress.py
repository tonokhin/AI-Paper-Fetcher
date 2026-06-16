from pathlib import Path
import tempfile
import unittest

from ai_paper_fetcher.progress import (
    LearningProgress,
    find_next_papers,
    load_progress,
    save_progress,
    update_progress,
)
from ai_paper_fetcher.models import Paper


def paper(paper_id: str = "paper-1") -> Paper:
    return Paper(
        paper_id=paper_id,
        title=f"Paper {paper_id}",
        authors="",
        published_date="",
        updated_date="",
        abstract="",
        categories="",
        topic="",
        pdf_url="",
    )


class ProgressTests(unittest.TestCase):
    def test_update_and_load_progress(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "learning_progress.json"
            progress = {}

            update_progress(
                progress,
                "paper-1",
                status="reading",
                understanding=3,
                interest="high",
                time_spent_minutes=25,
                next_action="Read experiments.",
                note="The setup is clear.",
            )
            save_progress(path, progress)
            loaded = load_progress(path)

        self.assertEqual(loaded["paper-1"].status, "reading")
        self.assertEqual(loaded["paper-1"].understanding, 3)
        self.assertEqual(loaded["paper-1"].interest, "high")
        self.assertEqual(loaded["paper-1"].time_spent_minutes, 25)
        self.assertEqual(loaded["paper-1"].next_action, "Read experiments.")
        self.assertEqual(loaded["paper-1"].notes, ["The setup is clear."])

    def test_find_next_papers_skips_completed_items(self):
        progress = {
            "paper-1": LearningProgress(paper_id="paper-1", status="understood"),
            "paper-2": LearningProgress(paper_id="paper-2", status="reading"),
        }

        result = find_next_papers([paper("paper-1"), paper("paper-2"), paper("paper-3")], progress, limit=2)

        self.assertEqual([item.paper_id for item in result], ["paper-2", "paper-3"])


if __name__ == "__main__":
    unittest.main()
