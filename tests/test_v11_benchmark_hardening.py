from __future__ import annotations

import hashlib
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SameCaseNormalizationTests(unittest.TestCase):
    def test_embedded_source_case_is_excluded(self):
        module = load_module("retrieve_cross_case_patterns")
        signature = {"output": ["coverage"], "keywords": ["geometry"], "forbidden_source_cases": ["2023B"]}
        library = {
            "version": 1,
            "cards": [
                {"id": "X19", "source_case": "CUMCM2023B-JMMIA-2024-01-10", "provenance": "verified", "kind": "move", "tags": ["geometry"], "move": "geometry", "reconstruction_test": "test", "counterfactual": "base", "failure_risk": "risk"},
                {"id": "X20", "source_case": "CUMCM2022B-OTHER", "provenance": "verified", "kind": "move", "tags": ["geometry"], "move": "geometry", "reconstruction_test": "test", "counterfactual": "base", "failure_risk": "risk"}
            ]
        }
        report = module.inspect(signature, library, 3)
        self.assertNotIn("X19", {item["id"] for item in report["selected"]})
        self.assertIn("X20", {item["id"] for item in report["selected"]})
        self.assertEqual(["2023B"], report["diagnostics"]["normalized_forbidden_source_cases"])


class HistoricalMemoryBoundaryTests(unittest.TestCase):
    def test_unknown_memory_is_limitation_not_strict_failure(self):
        module = load_module("audit_benchmark_isolation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "strategy.json"
            artifact.write_text("{}\n", encoding="utf-8")
            payload = {
                "version": 1,
                "benchmark_id": "case",
                "evaluation_mode": "retrospective_historical",
                "case_id": "2025B",
                "prior_model_memory": "unknown",
                "stage": "frozen",
                "pre_freeze_resources": [{"locator": "official.pdf", "category": "official_problem", "case_scope": ["2025B"]}],
                "frozen_artifacts": [{"path": "strategy.json", "sha256": digest(artifact)}],
                "frozen_at": "2026-08-10T00:00:00Z",
                "unblinded_at": None,
                "declared_solution_blind": False,
            }
            report = module.inspect(payload, root)
        memory = next(item for item in report["findings"] if item["code"] == "MODEL_MEMORY_UNKNOWN")
        self.assertEqual("Minor", memory["severity"])
        self.assertEqual("solution_isolated_historical_candidate", report["evidence_label"])


class OutputClosureTests(unittest.TestCase):
    def manifest(self, root: Path) -> dict:
        pre = root / "pre-pilot.json"
        pre.write_text(json.dumps({"shortlisted": ["I1", "I2", "I3"], "thresholds": [1, 2, 3]}), encoding="utf-8")
        result = root / "result.json"
        result.write_text(json.dumps({"q2": {"policy": [{"group": 1, "week": 12}]}}), encoding="utf-8")
        return {
            "version": 1,
            "case_id": "2025C",
            "created_at": "2026-08-10T00:20:00Z",
            "pre_pilot_manifest": {"path": "pre-pilot.json", "sha256": digest(pre), "frozen_at": "2026-08-10T00:00:00Z", "first_pilot_started_at": "2026-08-10T00:05:00Z"},
            "requirements": [{"id": "Q2-policy", "official_locator": "problem p1 Q2", "required": True, "status": "complete", "artifact_path": "result.json", "artifact_sha256": digest(result), "content_checks": [{"type": "json_pointer_nonempty", "pointer": "/q2/policy"}]}]
        }

    def test_closed_output_and_pre_pilot_freeze_pass(self):
        module = load_module("audit_benchmark_output_closure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = module.inspect(self.manifest(root), root)
        self.assertEqual("pass", report["status"])
        self.assertEqual(1, report["closed_requirement_count"])

    def test_missing_required_output_blocks(self):
        module = load_module("audit_benchmark_output_closure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.manifest(root)
            payload["requirements"][0]["status"] = "missing"
            report = module.inspect(payload, root)
        self.assertIn("OFFICIAL_OUTPUT_INCOMPLETE", {item["code"] for item in report["findings"]})

    def test_post_pilot_freeze_blocks(self):
        module = load_module("audit_benchmark_output_closure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.manifest(root)
            payload["pre_pilot_manifest"]["frozen_at"] = "2026-08-10T00:10:00Z"
            report = module.inspect(payload, root)
        self.assertIn("PILOT_FREEZE_ORDER", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
