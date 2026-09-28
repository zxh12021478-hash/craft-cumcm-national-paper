from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AbstractCorpusAndOutlineIsolationTests(unittest.TestCase):
    def test_corpus_provenance_is_complete_unique_and_text_free(self):
        ledger = json.loads(
            (ROOT / "assets" / "benchmarks" / "abstract-corpus-provenance-2016-2025.json")
            .read_text(encoding="utf-8")
        )
        records = ledger["records"]
        self.assertEqual(ledger["knowledge_version"], "v20")
        self.assertEqual(len(records), 134)
        self.assertEqual(len({row["pdf_sha256"] for row in records}), 134)
        self.assertEqual(len({row["paper_id"] for row in records}), 134)
        self.assertTrue(all(row["semantic_review_status"] == "completed" for row in records))
        self.assertTrue(all(row["extraction_status"] == "extracted" for row in records))
        self.assertTrue(all(row["award_status"] == "not_established_from_local_file" for row in records))
        self.assertTrue(all("abstract" not in row for row in records))
        self.assertEqual(
            Counter(row["year"] for row in records),
            Counter({2016: 15, 2017: 18, 2018: 13, 2019: 17, 2020: 17,
                     2021: 17, 2022: 11, 2023: 5, 2024: 16, 2025: 5}),
        )
        self.assertEqual(Counter(row["extraction_method"] for row in records),
                         Counter({"pypdf": 46, "vision-ocr": 88}))

    def test_abstract_decisions_are_evidence_first_and_not_a_fact_source(self):
        decisions = (ROOT / "references" / "abstract-writing-decisions-2016-2025.md").read_text(
            encoding="utf-8"
        )
        protocol = (ROOT / "references" / "abstract-reconstruction-protocol.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "never a source of facts",
            "Select answers before methods",
            "Use numerical hierarchy",
            "Keep evidence adjacent",
            "Describe innovation by consequence",
            "Corpus-derived anti-patterns",
            "must not influence the pre-draft",
        ):
            with self.subTest(required=required):
                self.assertIn(required, decisions)
        self.assertIn("abstract-writing-decisions-2016-2025.md", protocol)
        self.assertIn("corpus preference loses", protocol)

    def test_outline_preferences_are_advisory_and_have_no_fixed_quotas(self):
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        problem_stage = (ROOT / "static" / "fragments" / "stage-problem-reading.md").read_text(
            encoding="utf-8"
        )
        combined = "\n".join((handoff, delivery, problem_stage))
        for required in (
            "题型适配、模型主线与高价值可视化建议",
            "求解真实性、验证闭环与成文质量建议",
            "three-dimensional figure is optional",
            "three genuinely meaningful dimensions",
            "All presentation suggestions are advisory",
            "no pseudocode",
        ):
            with self.subTest(required=required):
                self.assertIn(required, combined)
        for banned in (
            r"至少\s*3\s*个伪代码",
            r"3D.{0,12}不少于\s*3",
            r"4\s*[-—~～]\s*5\s*张",
            r"附录.{0,8}3\s*[-—~～]\s*4\s*页",
            r"摘要.{0,8}充满.{0,8}第一页",
        ):
            with self.subTest(banned=banned):
                self.assertIsNone(re.search(banned, combined, re.I))

    def test_two_knowledge_tracks_are_routed_separately(self):
        decisions = (ROOT / "references" / "abstract-writing-decisions-2016-2025.md").read_text(
            encoding="utf-8"
        )
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        self.assertNotIn("建议的证据与呈现重点", decisions)
        self.assertNotIn("abstract-corpus-provenance-2016-2025", handoff)
        self.assertNotIn("2016--2025", handoff)
        self.assertIn("must not influence the pre-draft", decisions)


if __name__ == "__main__":
    unittest.main()
