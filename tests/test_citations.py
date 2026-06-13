import unittest

from ai_paper_fetcher.citations import _title_similarity


class CitationTests(unittest.TestCase):
    def test_title_similarity_matches_same_title_with_spacing_changes(self):
        score = _title_similarity("A Test Paper for LLM Evaluation", "A test paper  for llm evaluation")

        self.assertGreater(score, 0.95)

    def test_title_similarity_rejects_different_title(self):
        score = _title_similarity("A Test Paper for LLM Evaluation", "Quantum chemistry simulation")

        self.assertLess(score, 0.82)


if __name__ == "__main__":
    unittest.main()
