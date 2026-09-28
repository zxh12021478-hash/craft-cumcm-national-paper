from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def dimensions(score: float = 3.0) -> dict:
    names = (
        "requirement_coverage",
        "formulation_validity",
        "structural_insight",
        "reproducibility",
        "independent_validation",
        "cross_artifact_consistency",
        "decision_value",
    )
    return {name: {"score": score, "evidence": [f"artifact evidence for {name}"]} for name in names}


def benchmark_case(root: Path, case_id: str = "synthetic-opt") -> dict:
    artifact = root / f"{case_id}.json"
    artifact.write_text(json.dumps({"strategy": "frozen", "case": case_id}), encoding="utf-8")
    return {
        "case_id": case_id,
        "task_family": "optimization-scheduling",
        "isolation_label": "synthetic_forward_test",
        "evidence_level": "E1",
        "frozen_artifact": {
            "file": artifact.name,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        },
        "frozen_before_unblinding": True,
        "self_assessment": {"dimensions": dimensions(3.5)},
        "independent_assessment": {
            "reviewer_type": "independent_ai",
            "reviewers": ["independent evaluator"],
            "assessed_at": "2026-08-09T12:30:00-07:00",
            "dimensions": dimensions(3.0),
        },
        "automatic_failures": [],
        "elapsed_minutes": 20,
        "human_interventions": 0,
    }


class CapabilityBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("score_capability_benchmarks")

    def test_frozen_independent_case_passes_but_remains_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {
                "version": 1,
                "created_at": "2026-08-09T12:00:00-07:00",
                "cases": [benchmark_case(root)],
            }
            report = self.module.inspect(
                payload,
                root,
                ROOT / "assets" / "schemas" / "capability-benchmark-ledger.schema.json",
            )
            self.assertEqual("PASS", report["cases"][0]["status"])
            self.assertEqual("diagnostic_only", report["status"])
            self.assertEqual(1.0, report["metrics"]["independent_pass_rate"])
            self.assertIsNone(report["award_prediction"])

    def test_hash_mismatch_is_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case = benchmark_case(root)
            case["frozen_artifact"]["sha256"] = "0" * 64
            payload = {"version": 1, "created_at": "2026-08-09T12:00:00-07:00", "cases": [case]}
            report = self.module.inspect(payload, root)
            self.assertEqual("blocked", report["status"])
            self.assertIn("FROZEN_HASH_MISMATCH", {item["code"] for item in report["findings"]})

    def test_self_only_case_cannot_count_as_independent_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case = benchmark_case(root)
            case["independent_assessment"] = None
            payload = {"version": 1, "created_at": "2026-08-09T12:00:00-07:00", "cases": [case]}
            report = self.module.inspect(payload, root)
            self.assertEqual("SELF_ONLY", report["cases"][0]["status"])
            self.assertEqual(0, report["metrics"]["independently_assessed_cases"])

    def test_broad_evidence_requires_family_coverage_and_prospective_cases(self):
        families = [
            "evaluation-ranking",
            "forecasting-optimization",
            "classification-warning",
            "optimization-scheduling",
            "mechanism-simulation",
            "network-spatial",
            "sequential-control",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = []
            for index, family in enumerate(families):
                case = benchmark_case(root, f"prospective-{index}")
                case["task_family"] = family
                case["isolation_label"] = "prospective_canary"
                case["evidence_level"] = "E2"
                cases.append(case)
            payload = {"version": 1, "created_at": "2026-08-09T12:00:00-07:00", "cases": cases}
            report = self.module.inspect(payload, root)
            self.assertEqual("broad_capability_evidence", report["status"])
            self.assertEqual(7, report["metrics"]["task_family_count"])
            self.assertEqual(7, report["metrics"]["prospective_case_count"])


class PreFreezeIsolationLedgerTests(unittest.TestCase):
    def test_honest_pre_freeze_ledger_is_initialized_not_frozen(self):
        module = load_module("audit_benchmark_isolation")
        payload = {
            "version": 1,
            "benchmark_id": "cumcm-2025-b",
            "evaluation_mode": "retrospective_historical",
            "case_id": "2025B",
            "prior_model_memory": "unknown",
            "stage": "pre_freeze",
            "pre_freeze_resources": [
                {
                    "locator": "https://www.mcm.edu.cn/official-problem-page",
                    "category": "official_problem",
                    "case_scope": ["2025B"],
                }
            ],
            "frozen_artifacts": [],
            "frozen_at": None,
            "unblinded_at": None,
            "declared_solution_blind": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            report = module.inspect(
                payload,
                Path(directory),
                ROOT / "assets" / "schemas" / "benchmark-isolation-ledger.schema.json",
            )
        codes = {item["code"] for item in report["findings"]}
        self.assertEqual("pre_freeze_initialized", report["evidence_label"])
        self.assertIn("FREEZE_PENDING", codes)
        self.assertFalse(any(item["severity"] == "Blocker" for item in report["findings"]))


class StrongerTruthHarnessTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("truth_harness")

    def test_objective_and_matrix_are_recomputed_from_primitives(self):
        payload = {
            "version": 1,
            "checks": [
                {
                    "id": "objective",
                    "family": "optimization-scheduling",
                    "type": "linear_objective_recompute",
                    "coefficients": [2, 3],
                    "variables": [4, 5],
                    "constant": 1,
                    "reported_objective": 24,
                },
                {
                    "id": "constraints",
                    "family": "optimization-scheduling",
                    "type": "matrix_constraint_recompute",
                    "matrix": [[1, 1], [2, -1]],
                    "variables": [4, 5],
                    "lower_bounds": [None, 3],
                    "upper_bounds": [9, None],
                },
            ],
        }
        report = self.module.inspect(payload, ROOT)
        self.assertEqual([], report["findings"])

    def test_wrong_reported_objective_fails(self):
        payload = {
            "version": 1,
            "checks": [
                {
                    "id": "bad-objective",
                    "family": "optimization-scheduling",
                    "type": "linear_objective_recompute",
                    "coefficients": [2, 3],
                    "variables": [4, 5],
                    "constant": 1,
                    "reported_objective": 25,
                }
            ],
        }
        report = self.module.inspect(payload, ROOT)
        self.assertIn("TRUTH_CHECK_FAILED", {item["code"] for item in report["findings"]})


class ProgressiveDisclosureTests(unittest.TestCase):
    def test_every_manifest_family_route_exists(self):
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        expected = [
            "task-family-evaluation-ranking.md",
            "task-family-forecasting-optimization.md",
            "task-family-classification-warning.md",
            "task-family-optimization-scheduling.md",
            "task-family-mechanism-simulation.md",
            "task-family-network-spatial.md",
            "task-family-sequential-control.md",
        ]
        for filename in expected:
            with self.subTest(filename=filename):
                self.assertIn(filename, manifest)
                self.assertTrue((ROOT / "references" / filename).is_file())


if __name__ == "__main__":
    unittest.main()
