from pathlib import Path
import tempfile
import unittest

from ai_paper_fetcher.config import load_foundational_papers, load_topics


class ConfigTests(unittest.TestCase):
    def test_load_topics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                """
topics:
  llm_evaluation:
    query: "LLM evaluation"
    include_keywords:
      - benchmark
    exclude_keywords:
      - survey
    categories:
      - cs.CL
    published_after: "2026-01-01"
""",
                encoding="utf-8",
            )

            topics = load_topics(config_path)

        topic = topics["llm_evaluation"]
        self.assertEqual(topic.query, "LLM evaluation")
        self.assertEqual(topic.include_keywords, ["benchmark"])
        self.assertEqual(topic.exclude_keywords, ["survey"])
        self.assertEqual(topic.categories, ["cs.CL"])
        self.assertEqual(topic.published_after, "2026-01-01")

    def test_load_foundational_papers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "foundational_papers.yaml"
            config_path.write_text(
                """
papers:
  - title: "Attention Is All You Need"
    arxiv_id: "1706.03762"
    topic: "foundations_transformers"
    note: "Introduced the Transformer."
""",
                encoding="utf-8",
            )

            papers = load_foundational_papers(config_path)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Attention Is All You Need")
        self.assertEqual(papers[0].arxiv_id, "1706.03762")
        self.assertEqual(papers[0].topic, "foundations_transformers")
        self.assertEqual(papers[0].note, "Introduced the Transformer.")


if __name__ == "__main__":
    unittest.main()
