from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SingleHandoffTests(unittest.TestCase):
    def test_writer_receives_one_generated_document(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        self.assertIn("exactly one user-facing", skill)
        self.assertIn("one non-binding `推荐解题思路大纲`", skill)
        self.assertIn("Export exactly one generated handoff document", handoff)
        self.assertIn("`推荐解题思路大纲.md`", handoff)

    def test_internal_ledgers_are_not_external_clutter(self):
        workflow = (ROOT / "static" / "core-workflow.md").read_text(encoding="utf-8")
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        self.assertIn("Do not provide a solver contract", workflow)
        self.assertIn("return-package requirements", delivery)
        self.assertIn("not comprehensive or", delivery)

    def test_pre_draft_output_is_the_only_generated_deliverable(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "static" / "core-workflow.md").read_text(encoding="utf-8")
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        self.assertIn("exactly one user-facing", skill)
        self.assertIn("This is the only user-facing deliverable before that", workflow)
        self.assertIn("Do not include full derivations", delivery)

    def test_outline_recommends_without_binding_writer(self):
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        self.assertIn("may be revised or rejected", handoff)
        self.assertIn("owns equations, algorithms, calculations, code", delivery)

    def test_single_document_has_actionable_sections(self):
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        for required in (
            "problem's central tension",
            "preferred overall direction",
            "primary and at most two supporting innovation ideas",
            "important validation directions",
            "central paper story",
            "advisory and may be revised or rejected",
        ):
            with self.subTest(required=required):
                self.assertIn(required, handoff)


if __name__ == "__main__":
    unittest.main()
