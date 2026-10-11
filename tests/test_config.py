from pathlib import Path
import tempfile
import unittest

from ai_paper_fetcher.config import load_foundational_papers, load_topics, load_tracks


class ConfigTests(unittest.TestCase):
    def test_adaptive_data_analysis_topic_is_in_ai_track(self):
        root = Path(__file__).resolve().parents[1]
        topics = load_topics(root / "config.yaml")
        tracks = load_tracks(root / "config.yaml")

        topic = topics["adaptive_data_analysis"]
        self.assertEqual(topic.query, "holdout")
        self.assertIn("reusable holdout", topic.include_keywords)
        self.assertIn("stat.ML", topic.categories)
        self.assertIn("adaptive_data_analysis", tracks["ai"].topics)

    def test_llm_benchmark_contamination_topic_is_in_ai_track(self):
        root = Path(__file__).resolve().parents[1]
        topics = load_topics(root / "config.yaml")
        tracks = load_tracks(root / "config.yaml")

        topic = topics["llm_benchmark_contamination"]
        self.assertEqual(topic.query, "contamination")
        self.assertIn("evaluation data contamination", topic.include_keywords)
        self.assertIn("cs.CR", topic.categories)
        self.assertIn("llm_benchmark_contamination", tracks["ai"].topics)

    def test_synthetic_data_feedback_topic_is_in_ai_track(self):
        root = Path(__file__).resolve().parents[1]
        topics = load_topics(root / "config.yaml")
        tracks = load_tracks(root / "config.yaml")

        topic = topics["synthetic_data_feedback"]
        self.assertEqual(topic.query, "model collapse")
        self.assertIn("recursive training", topic.include_keywords)
        self.assertIn("cs.CL", topic.categories)
        self.assertIn("synthetic_data_feedback", tracks["ai"].topics)

    def test_human_ai_interaction_topic_is_in_ai_track(self):
        root = Path(__file__).resolve().parents[1]
        topics = load_topics(root / "config.yaml")
        tracks = load_tracks(root / "config.yaml")

        topic = topics["human_ai_interaction"]
        self.assertEqual(topic.query, "human-AI interaction")
        self.assertIn("human-LLM interaction", topic.include_keywords)
        self.assertIn("cs.HC", topic.categories)
        self.assertIn("human_ai_interaction", tracks["ai"].topics)

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

    def test_load_tracks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                """
tracks:
  ai:
    topics:
      - llm_evaluation
      - ai_agents
  fundamentals:
    - algorithms
    - mathematics_for_ai
""",
                encoding="utf-8",
            )

            tracks = load_tracks(config_path)

        self.assertEqual(tracks["ai"].topics, ["llm_evaluation", "ai_agents"])
        self.assertEqual(tracks["fundamentals"].topics, ["algorithms", "mathematics_for_ai"])


if __name__ == "__main__":
    unittest.main()
