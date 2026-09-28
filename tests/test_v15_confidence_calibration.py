from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConfidenceCalibrationTests(unittest.TestCase):
    def test_external_agent_uses_scoped_confidence(self):
        protocol = (ROOT / "references" / "ai-baseline-regression-protocol.md").read_text(encoding="utf-8")
        self.assertIn("Scoped provisional confidence", protocol)
        self.assertIn("`high`", protocol)
        self.assertIn("`standard`", protocol)
        self.assertIn("`low`", protocol)
        self.assertIn("Model identity may inform the prior but cannot determine the tier by itself", protocol)

    def test_quarantine_is_not_blanket_distrust(self):
        protocol = (ROOT / "references" / "ai-baseline-regression-protocol.md").read_text(encoding="utf-8")
        stage = (ROOT / "static" / "fragments" / "stage-external-baseline-handoff.md").read_text(encoding="utf-8")
        self.assertIn("not that its author is presumed incompetent", protocol)
        self.assertIn("not a judgment that the external agent is weak", stage)

    def test_high_confidence_preserves_strong_work_but_verifies_core(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        self.assertIn("Retain low-risk prose and structure", skill)
        self.assertIn("independently verify the core claims", skill)
        self.assertIn("greater reuse and less repetitive low-risk", handoff)

    def test_different_writer_route_is_not_a_defect(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        self.assertIn("different route as a defect", skill)
        self.assertIn("do not penalize it merely", handoff)


if __name__ == "__main__":
    unittest.main()
