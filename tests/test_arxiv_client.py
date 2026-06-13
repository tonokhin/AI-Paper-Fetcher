import unittest

from ai_paper_fetcher.arxiv_client import build_search_query, extract_arxiv_id, parse_arxiv_feed


SAMPLE_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345v2</id>
    <updated>2024-01-05T00:00:00Z</updated>
    <published>2024-01-01T00:00:00Z</published>
    <title>  A Test Paper\nfor LLM Evaluation </title>
    <summary> This paper tests benchmarks. </summary>
    <author><name>Ada Lovelace</name></author>
    <author><name>Alan Turing</name></author>
    <category term="cs.CL" />
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1234/example</arxiv:doi>
    <link title="pdf" href="https://arxiv.org/pdf/2401.12345" />
  </entry>
</feed>
"""


class ArxivClientTests(unittest.TestCase):
    def test_extract_arxiv_id_removes_version(self):
        self.assertEqual(extract_arxiv_id("http://arxiv.org/abs/2401.12345v2"), "2401.12345")

    def test_parse_arxiv_feed(self):
        papers = parse_arxiv_feed(SAMPLE_FEED, "LLM evaluation")

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].paper_id, "2401.12345")
        self.assertEqual(papers[0].title, "A Test Paper for LLM Evaluation")
        self.assertEqual(papers[0].authors, "Ada Lovelace, Alan Turing")
        self.assertEqual(papers[0].categories, "cs.CL")
        self.assertEqual(papers[0].pdf_url, "https://arxiv.org/pdf/2401.12345")
        self.assertEqual(papers[0].doi, "10.1234/example")

    def test_build_search_query_with_categories(self):
        query = build_search_query("LLM evaluation", ["cs.CL", "cs.AI"])

        self.assertEqual(query, 'all:"LLM evaluation" AND (cat:cs.CL OR cat:cs.AI)')


if __name__ == "__main__":
    unittest.main()
