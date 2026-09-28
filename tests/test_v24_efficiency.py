from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EfficiencyRoutingTests(unittest.TestCase):
    def test_manifest_has_one_small_runtime_core(self):
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 25", manifest)
        self.assertIn("static/runtime-core.md", manifest)
        self.assertNotIn("  - static/core-principles.md", manifest)
        self.assertNotIn("  - static/core-workflow.md", manifest)
        self.assertNotIn("  - static/core-delivery.md", manifest)
        self.assertIn("efficiency-control", manifest)
        self.assertIn("plan_incremental_audit.py", manifest)

    def test_skill_prioritizes_value_per_time_and_token_without_weakening_gates(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        runtime = (ROOT / "static/runtime-core.md").read_text(encoding="utf-8")
        self.assertIn("per unit of contest", skill)
        self.assertIn("Codex token", skill)
        self.assertIn("Never save tokens by weakening", skill)
        self.assertIn("sprint", runtime)
        self.assertIn("standard", runtime)
        self.assertIn("final", runtime)
        self.assertIn("Soft output budgets never suppress", skill)

    def test_efficiency_profiles_keep_hard_floors(self):
        payload = json.loads(
            (ROOT / "assets/workflows/efficiency-profiles.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(payload["modes"]), {"sprint", "standard", "final"})
        self.assertLess(payload["modes"]["sprint"]["chat_soft_cap_zh_chars"],
                        payload["modes"]["standard"]["chat_soft_cap_zh_chars"])
        for required in ("correct_problem_interpretation", "valid_formulation",
                         "reproduced_headline_results", "independent_validation"):
            self.assertIn(required, payload["hard_floors"])

    def test_instruction_sets_pass_declared_budgets(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/measure_instruction_budget.py"), "--strict"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertLessEqual(report["sets"]["base"]["totals"]["words"], 3000)


class IncrementalAuditTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("plan_incremental_audit", "scripts/plan_incremental_audit.py")

    def test_no_change_reuses_verified_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old", root / "new"
            old.mkdir(); new.mkdir()
            (old / "paper.md").write_text("same", encoding="utf-8")
            (new / "paper.md").write_text("same", encoding="utf-8")
            report = self.module.build_report(old, new)
            self.assertEqual(report["audit_mode"], "none")
            self.assertEqual(report["review_scope"], [])

    def test_paper_delta_is_targeted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old", root / "new"
            old.mkdir(); new.mkdir()
            (old / "paper.md").write_text("before", encoding="utf-8")
            (new / "paper.md").write_text("after", encoding="utf-8")
            report = self.module.build_report(old, new)
            self.assertEqual(report["audit_mode"], "targeted")
            self.assertIn("cross_artifact_consistency", report["review_scope"])

    def test_code_delta_escalates_full(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old", root / "new"
            old.mkdir(); new.mkdir()
            (old / "solve.py").write_text("print(1)", encoding="utf-8")
            (new / "solve.py").write_text("print(2)", encoding="utf-8")
            report = self.module.build_report(old, new)
            self.assertEqual(report["audit_mode"], "full")
            self.assertIn("validation", report["review_scope"])


if __name__ == "__main__":
    unittest.main()
