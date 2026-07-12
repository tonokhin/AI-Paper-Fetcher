from pathlib import Path
import tempfile
import unittest

import yaml

from ai_paper_fetcher.curriculum_export import (
    CurriculumTopicMapping,
    export_curriculum_resources,
    load_curriculum_mapping,
    paper_to_resource,
    resource_id_for_paper,
)
from ai_paper_fetcher.models import Paper
from ai_paper_fetcher.storage import write_papers


def sample_paper() -> Paper:
    return Paper(
        paper_id="1706.03762v7",
        title="Attention Is All You Need",
        authors="Ashish Vaswani et al.",
        published_date="2017-06-12",
        updated_date="2023-08-02",
        abstract="Introduces the Transformer architecture.",
        categories="cs.CL",
        topic="foundations_transformers",
        pdf_url="https://arxiv.org/pdf/1706.03762",
        collection="foundational",
        reason_to_read="Foundational paper: Introduced the Transformer architecture.",
    )


def write_mapping(path: Path) -> None:
    path.write_text(
        """
topics:
  foundations_transformers:
    covers:
      - transformers-and-llms
    stage: graduate
    role: research
""",
        encoding="utf-8",
    )


class CurriculumExportTests(unittest.TestCase):
    def test_load_curriculum_mapping(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mapping_path = Path(temp_dir) / "mapping.yaml"
            write_mapping(mapping_path)

            mapping = load_curriculum_mapping(mapping_path)

        self.assertEqual(mapping["foundations_transformers"].covers, ["transformers-and-llms"])
        self.assertEqual(mapping["foundations_transformers"].stage, "graduate")
        self.assertEqual(mapping["foundations_transformers"].role, "research")

    def test_paper_to_resource_uses_curriculum_shape(self):
        resource = paper_to_resource(
            sample_paper(),
            CurriculumTopicMapping(covers=["transformers-and-llms"], stage="graduate"),
        )

        self.assertEqual(resource["id"], "paper-1706-03762")
        self.assertEqual(resource["title"], "Attention Is All You Need")
        self.assertEqual(resource["author"], "Ashish Vaswani et al.")
        self.assertEqual(resource["type"], "paper")
        self.assertEqual(resource["level"], "advanced")
        self.assertEqual(resource["cost"], "free")
        self.assertEqual(resource["format"], "text")
        self.assertEqual(resource["estimated_hours"], 6.0)
        self.assertEqual(resource["url"], "https://arxiv.org/abs/1706.03762")
        self.assertEqual(resource["covers"], ["transformers-and-llms"])
        self.assertEqual(resource["provenance"]["source"], "ai-paper-fetcher")
        self.assertEqual(resource["provenance"]["review_status"], "pending")

    def test_resource_id_for_non_arxiv_id_is_stable(self):
        paper = sample_paper()
        paper.paper_id = "custom/topic:paper"

        self.assertEqual(resource_id_for_paper(paper), "paper-custom-topic-paper")

    def test_export_curriculum_resources_writes_yaml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "data" / "reading_list.csv"
            mapping_path = root / "curriculum_mapping.yaml"
            output_path = root / "resources" / "generated-ai-papers.yaml"
            write_papers(csv_path, [sample_paper()])
            write_mapping(mapping_path)

            result = export_curriculum_resources(
                reading_list_path=csv_path,
                mapping_path=mapping_path,
                output_path=output_path,
            )

            data = yaml.safe_load(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.written, 1)
        self.assertEqual(data["resources"][0]["id"], "paper-1706-03762")
        self.assertEqual(data["resources"][0]["covers"], ["transformers-and-llms"])

    def test_export_fails_on_unmapped_topic_by_default(self):
        paper = sample_paper()
        paper.topic = "unmapped"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "data" / "reading_list.csv"
            mapping_path = root / "curriculum_mapping.yaml"
            output_path = root / "resources.yaml"
            write_papers(csv_path, [paper])
            write_mapping(mapping_path)

            with self.assertRaises(ValueError):
                export_curriculum_resources(
                    reading_list_path=csv_path,
                    mapping_path=mapping_path,
                    output_path=output_path,
                )

    def test_export_can_skip_unmapped_topics(self):
        paper = sample_paper()
        paper.topic = "unmapped"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "data" / "reading_list.csv"
            mapping_path = root / "curriculum_mapping.yaml"
            output_path = root / "resources.yaml"
            write_papers(csv_path, [paper])
            write_mapping(mapping_path)

            result = export_curriculum_resources(
                reading_list_path=csv_path,
                mapping_path=mapping_path,
                output_path=output_path,
                skip_unmapped=True,
            )
            data = yaml.safe_load(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.written, 0)
        self.assertEqual(result.skipped_unmapped, ["unmapped"])
        self.assertEqual(data["resources"], [])


if __name__ == "__main__":
    unittest.main()
