from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RoleBoundaryTests(unittest.TestCase):
    def test_skill_is_not_default_full_paper_author(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("A separate writing\nagent owns the first draft of the full paper body", skill)
        self.assertIn("Do not independently generate a full paper body", skill)
        self.assertIn("The abstract is the deliberate exception", skill)

    def test_paper_route_targets_abstract_and_writer_handoff(self):
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 25", manifest)
        self.assertIn("write_abstract", manifest)
        self.assertIn("build_writer_handoff", manifest)
        self.assertIn("review_writer_draft", manifest)
        self.assertNotIn("write_paper", manifest)
        self.assertNotIn("rewrite_paper", manifest)

    def test_final_packaging_remains_owned(self):
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        self.assertIn("Start from the separate writing agent's draft", delivery)
        for required in ("final electronic paper", "runnable code", "AI-use disclosure", "validator reports"):
            with self.subTest(required=required):
                self.assertIn(required, delivery)

    def test_abstract_gate_requires_answers_innovation_and_validation(self):
        stage = (ROOT / "static" / "fragments" / "stage-paper-writing.md").read_text(encoding="utf-8")
        self.assertIn("action → method/mechanism → canonical answer", stage)
        self.assertIn("baseline limitation → structural change → measured consequence", stage)
        self.assertIn("independent validation or robustness result", stage)
        self.assertIn("frozen result ledger", stage)


if __name__ == "__main__":
    unittest.main()
