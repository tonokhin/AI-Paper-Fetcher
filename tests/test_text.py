import unittest

from ai_paper_fetcher.text import safe_filename, slugify


class TextTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("LLM Evaluation!"), "llm_evaluation")

    def test_safe_filename(self):
        self.assertEqual(safe_filename("2401.1: A/B Test?"), "2401.1_A_B_Test")


if __name__ == "__main__":
    unittest.main()
