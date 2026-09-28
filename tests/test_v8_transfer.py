from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class CrossCaseRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("retrieve_cross_case_patterns")
        self.library = json.loads(
            (
                ROOT
                / "assets"
                / "benchmarks"
                / "cross-case-structural-patterns.json"
            ).read_text(encoding="utf-8")
        )
        self.award_evidence = json.loads(
            (
                ROOT
                / "assets"
                / "benchmarks"
                / "official-award-evidence.json"
            ).read_text(encoding="utf-8")
        )

    def test_routing_signature_returns_diverse_cases(self):
        signature = {
            "output": ["routing", "optimization"],
            "structures": ["graph", "sequential_decision"],
            "constraints": ["capacity", "time_window"],
            "bottlenecks": ["solver_scale"],
            "validation": ["exact_small_instance", "certificate"],
            "forbidden_source_cases": ["CUMCM2024A-A163"],
        }
        report = self.module.inspect(
            signature,
            self.library,
            5,
            self.award_evidence,
        )
        self.assertGreaterEqual(report["diagnostics"]["distinct_source_cases"], 2)
        self.assertNotIn(
            "CUMCM2024A-A163",
            {item["source_case"] for item in report["selected"]},
        )
        self.assertLessEqual(len(report["selected"]), 5)

    def test_high_accuracy_signature_forces_guardrail(self):
        signature = {
            "output": ["classification"],
            "structures": ["repeated_measure"],
            "bottlenecks": ["small_sample", "high_accuracy", "leakage"],
        }
        report = self.module.inspect(
            signature,
            self.library,
            4,
            self.award_evidence,
        )
        self.assertTrue(report["diagnostics"]["guardrail_required"])
        self.assertTrue(report["diagnostics"]["guardrail_present"])
        self.assertIn("G01", {item["id"] for item in report["selected"]})

    def test_award_evidence_links_are_closed(self):
        errors = self.module.validate_award_links(
            self.library,
            self.award_evidence,
        )
        self.assertEqual([], errors)
        self.assertEqual(24, len(self.library["cards"]))
        self.assertEqual(
            10,
            sum(
                (card.get("award_verification") or {}).get("status")
                == "verified"
                for card in self.library["cards"]
            ),
        )
        self.assertEqual(
            set(range(2020, 2026)),
            {record["year"] for record in self.award_evidence["records"]},
        )

    def test_award_bonus_is_modest_and_requires_evidence(self):
        signature = {
            "output": ["decision"],
            "structures": ["uncertainty_decision", "sequential_decision"],
            "constraints": ["cost"],
            "validation": ["expected_utility"],
        }
        card = next(card for card in self.library["cards"] if card["id"] == "X04")
        raw, _ = self.module.score(card, signature, award_verified=False)
        verified, _ = self.module.score(card, signature, award_verified=True)
        self.assertGreater(raw, 0)
        self.assertAlmostEqual(raw * 1.08, verified)

        report_without_ledger = self.module.inspect(signature, self.library, 5)
        x04 = next(
            item for item in report_without_ledger["selected"] if item["id"] == "X04"
        )
        self.assertFalse(x04["award_verified"])

    def test_display_only_card_is_not_promoted_to_award_verified(self):
        signature = {
            "output": ["routing"],
            "structures": ["geometry", "locality"],
            "validation": ["certificate"],
        }
        report = self.module.inspect(
            signature,
            self.library,
            7,
            self.award_evidence,
        )
        x01 = next(item for item in report["selected"] if item["id"] == "X01")
        self.assertFalse(x01["award_verified"])

    def test_broken_award_reference_is_detected(self):
        broken = json.loads(json.dumps(self.library))
        broken["cards"][3]["award_verification"]["evidence_id"] = "MISSING"
        errors = self.module.validate_award_links(broken, self.award_evidence)
        self.assertTrue(any("MISSING" in error for error in errors))


class TransferSchemaTests(unittest.TestCase):
    def test_optional_transfer_lineage_is_schema_valid(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema unavailable")
        schema = json.loads(
            (
                ROOT
                / "assets"
                / "schemas"
                / "innovation-tournament.schema.json"
            ).read_text(encoding="utf-8")
        )
        payload = json.loads(
            (
                ROOT
                / "assets"
                / "templates"
                / "结构洞察淘汰赛模板.json"
            ).read_text(encoding="utf-8")
        )
        payload["candidates"][0]["transfer_lineage"] = {
            "library_version": 1,
            "borrowed_moves": ["X01", "X11"],
            "target_reconstruction": "将局部危险集重构为当前题约束下的有限事件集合。",
            "noncopied_boundary": "未复制来源论文的文字、公式、图表、数据或代码。",
        }
        errors = list(Draft202012Validator(schema).iter_errors(payload))
        self.assertEqual([], errors)


class TournamentFreezeSemanticsTests(unittest.TestCase):
    def test_failed_discovery_shortlist_is_not_posthoc_override(self):
        module = load_module("innovation_tournament")
        weights = module.load_weights(
            ROOT / "assets" / "workflows" / "innovation-selector-weights.json"
        )
        payload = json.loads(
            (
                ROOT
                / "assets"
                / "templates"
                / "结构洞察淘汰赛模板.json"
            ).read_text(encoding="utf-8")
        )
        for index, candidate in enumerate(payload["candidates"]):
            score = 4 if index < 3 else 3
            candidate["ai_assessment"] = {
                name: score for name in module.DIMENSIONS
            }
        payload["selection"] = {
            "shortlisted": ["I1", "I2", "I3"],
            "primary_candidate": "I1",
            "supporting_candidates": ["I3"],
        }
        payload["candidates"][1]["minimum_experiment"]["status"] = "fail"
        payload["candidates"][1]["stage"] = "rejected"
        with tempfile.TemporaryDirectory() as directory:
            report = module.inspect(payload, Path(directory), "freeze", weights)
        self.assertNotIn(
            "SELECTOR_OVERRIDE",
            {item["code"] for item in report["findings"]},
        )


class CrossCaseIsolationTests(unittest.TestCase):
    def test_unrelated_raw_paper_is_downgraded_not_contaminated(self):
        module = load_module("audit_benchmark_isolation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frozen = root / "strategy.json"
            frozen.write_text('{"strategy":"frozen"}\n', encoding="utf-8")
            import hashlib

            payload = {
                "version": 1,
                "benchmark_id": "blind-2",
                "evaluation_mode": "cross_case_assisted_historical",
                "case_id": "MATHORCUP2026A",
                "prior_model_memory": "none_declared",
                "pre_freeze_resources": [
                    {
                        "locator": "/corpus/CUMCM2024A-paper.pdf",
                        "category": "cross_case_raw_paper",
                        "case_scope": ["CUMCM2024A"],
                    }
                ],
                "frozen_artifacts": [
                    {
                        "path": "strategy.json",
                        "sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
                    }
                ],
                "frozen_at": "2026-07-30T20:00:00Z",
                "unblinded_at": None,
                "declared_solution_blind": False,
            }
            report = module.inspect(
                payload,
                root,
                ROOT / "assets" / "schemas" / "benchmark-isolation-ledger.schema.json",
            )
        self.assertEqual(
            "cross_case_assisted_solution_isolated_historical_candidate",
            report["evidence_label"],
        )
        self.assertNotIn(
            "BENCHMARK_CONTAMINATED",
            {item["code"] for item in report["findings"]},
        )


if __name__ == "__main__":
    unittest.main()
