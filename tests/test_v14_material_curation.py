from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MaterialCurationTests(unittest.TestCase):
    def test_validation_rejects_universal_checklists(self):
        playbook = (ROOT / "references" / "validation-playbook.md").read_text(encoding="utf-8")
        self.assertIn("Select evidence from the claim's failure path", playbook)
        self.assertIn("do not count a sensitivity plot as proof", playbook)
        self.assertIn("Never invent a universal `pass` threshold", playbook)
        for family in ("prediction and classification", "ranking and evaluation", "deterministic optimization", "mechanism and simulation"):
            with self.subTest(family=family):
                self.assertIn(family, playbook)

    def test_visual_rules_reject_template_artifacts(self):
        standard = (ROOT / "references" / "visualization-standards.md").read_text(encoding="utf-8")
        self.assertIn("Every node must correspond to an actual input", standard)
        self.assertIn("perspective-distorting 3D bars", standard)
        self.assertIn("Use radar charts only when", standard)

    def test_terminal_checklist_carries_new_gates(self):
        checklist = (ROOT / "assets" / "templates" / "国奖论文终检清单.yaml").read_text(encoding="utf-8")
        for required in (
            "validation_matches_claim_and_plausible_failure_path",
            "sensitivity_not_substituted_for_formulation_or_solver_validation",
            "flowchart_nodes_and_edges_match_implemented_artifacts",
            "chart_geometry_does_not_distort_magnitude_or_imply_false_comparability",
        ):
            with self.subTest(required=required):
                self.assertIn(required, checklist)


if __name__ == "__main__":
    unittest.main()
