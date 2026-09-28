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


def scored_tournament(root: Path, freeze: bool = False) -> dict:
    payload = json.loads(
        (ROOT / "assets" / "templates" / "结构洞察淘汰赛模板.json").read_text(encoding="utf-8")
    )
    for index, candidate in enumerate(payload["candidates"]):
        score = 4 if index < 3 else 3
        candidate["ai_assessment"] = {
            "specificity": score,
            "necessity": score,
            "evidenceability": score,
            "consequence": score,
            "feasibility": score,
            "independence": score,
            "paper_value": score,
        }
    if not freeze:
        return payload
    payload["selection"] = {
        "shortlisted": ["I1", "I2", "I3"],
        "primary_candidate": "I1",
        "supporting_candidates": ["I2"],
    }
    decisions = {
        "I1": "selected_primary",
        "I2": "selected_supporting",
        "I3": "rejected",
    }
    for identifier in payload["selection"]["shortlisted"]:
        candidate = next(item for item in payload["candidates"] if item["id"] == identifier)
        evidence = root / "pilots" / f"{identifier}.json"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(
            json.dumps({"candidate": identifier, "pilot": "independent", "passed": True}),
            encoding="utf-8",
        )
        candidate["minimum_experiment"].update(
            {
                "status": "pass",
                "evidence_file": str(evidence.relative_to(root)),
                "evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                "observed_result": "预注册指标达到阈值且独立复核一致",
            }
        )
        candidate["stage"] = "validated"
        candidate["team_review"] = {
            "reviewed_by": ["队员甲", "队员乙"],
            "reviewed_at": "2026-09-04T20:00:00+08:00",
            "decision": decisions[identifier],
            "rationale": "依据题面证据、独立微型实验和比赛时限作出人工决定。",
        }
    return payload


class InnovationTournamentTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("innovation_tournament")
        self.weights = self.module.load_weights(
            ROOT / "assets" / "workflows" / "innovation-selector-weights.json"
        )

    def test_discovery_requires_eight_scored_structural_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.module.inspect(scored_tournament(root), root, "discovery", self.weights)
            self.assertTrue(report["summary"]["passed"])
            self.assertEqual(["I1", "I2", "I3"], report["recommended_shortlist"])
            self.assertEqual([], report["findings"])

    def test_generic_algorithm_tuning_is_rejected_as_innovation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = scored_tournament(root)
            candidate = payload["candidates"][-1]
            candidate["title"] = "改进遗传算法"
            candidate["insight_sentence"] = "通过自适应交叉概率提升遗传算法搜索效率和最终结果质量。"
            candidate["exact_modification"] = "只动态调整交叉和变异概率，不改变原问题的目标函数与约束。"
            candidate["mathematical_object_changes"] = ["solver"]
            report = self.module.inspect(payload, root, "discovery", self.weights)
            self.assertIn(
                "GENERIC_ALGORITHM_INNOVATION",
                {item["code"] for item in report["findings"]},
            )

    def test_freeze_binds_all_three_pilots_and_human_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.module.inspect(scored_tournament(root, True), root, "freeze", self.weights)
            severe = [
                item
                for item in report["findings"]
                if item["severity"] in {"Blocker", "Critical"}
            ]
            self.assertEqual([], severe)
            self.assertTrue(report["summary"]["passed"])

    def test_freeze_rejects_stale_pilot_and_ai_reviewer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = scored_tournament(root, True)
            (root / "pilots" / "I1.json").write_text('{"changed":true}\n', encoding="utf-8")
            payload["candidates"][1]["team_review"]["reviewed_by"] = ["Codex"]
            report = self.module.inspect(payload, root, "freeze", self.weights)
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("SHORTLIST_EVIDENCE_HASH", codes)
            self.assertIn("NON_HUMAN_INNOVATION_REVIEW", codes)


class InnovationCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("calibrate_innovation_selector")
        self.weights = self.module.load_base_weights(
            ROOT / "assets" / "workflows" / "innovation-selector-weights.json"
        )

    def test_empty_ledger_cannot_claim_calibration(self):
        payload = json.loads(
            (ROOT / "assets" / "templates" / "创新盲测校准台账模板.json").read_text(encoding="utf-8")
        )
        report = self.module.inspect(payload, ROOT, self.weights)
        self.assertEqual("diagnostic_only", report["status"])
        self.assertEqual(
            report["base_weights"],
            report["recommended_weights"],
        )
        self.assertIn(
            "INSUFFICIENT_CALIBRATION",
            {item["code"] for item in report["findings"]},
        )

    def test_changed_frozen_tournament_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tournament_path = root / "frozen.json"
            tournament_path.write_text(
                json.dumps(scored_tournament(root, False)),
                encoding="utf-8",
            )
            payload = {
                "version": 1,
                "created_at": "2026-09-05T12:00:00+08:00",
                "cases": [
                    {
                        "case_id": "blind-01",
                        "isolation_label": "prospective_canary",
                        "frozen_tournament": {
                            "file": "frozen.json",
                            "sha256": "0" * 64,
                        },
                        "frozen_before_unblinding": True,
                        "human_review": {
                            "reviewers": ["队员甲"],
                            "reviewed_at": "2026-09-06T12:00:00+08:00",
                            "human_best_candidate": "I1",
                            "candidate_outcomes": [
                                {
                                    "candidate_id": identifier,
                                    "human_value_score": 4 if identifier == "I1" else 3,
                                    "implemented": identifier == "I1",
                                    "experiment_passed": True,
                                    "false_novelty": False,
                                    "selected_final": identifier == "I1",
                                    "actual_hours": 2,
                                    "decision_effect": 0.1,
                                    "notes": "由人工在解禁后复核。",
                                }
                                for identifier in ("I1", "I2", "I3")
                            ],
                        },
                        "unblinded_at": "2026-09-06T10:00:00+08:00",
                    }
                ],
            }
            report = self.module.inspect(payload, root, self.weights)
            self.assertIn(
                "TOURNAMENT_HASH_MISMATCH",
                {item["code"] for item in report["findings"]},
            )


class InnovationWorkflowTests(unittest.TestCase):
    def test_workflow_audit_registers_hash_bound_machine_evidence(self):
        workflow = load_module("cumcm_workflow")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow.init_project(root, "2026-A", None, "competition-lite")
            manifest = root / "strategy" / "innovation.json"
            manifest.write_text(json.dumps(scored_tournament(root, True)), encoding="utf-8")
            returncode, report = workflow.run_innovation_audit(
                root,
                str(manifest),
                "freeze",
                None,
            )
            self.assertEqual(0, returncode)
            self.assertTrue(report["summary"]["passed"])
            config = workflow.load_config(root)
            self.assertEqual(
                hashlib.sha256(manifest.read_bytes()).hexdigest(),
                config["artifacts"]["innovation_tournament"]["sha256"],
            )
            self.assertTrue(config["artifacts"]["innovation_report"]["passed"])

    def test_model_selection_rejects_forged_unbound_report(self):
        workflow = load_module("cumcm_workflow")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow.init_project(root, "2026-A", None, "competition-lite")
            evidence = root / "strategy" / "team-review.md"
            evidence.write_text("team review\n", encoding="utf-8")
            tournament = root / "strategy" / "innovation.json"
            tournament.write_text('{"problem_id":"2026-A"}\n', encoding="utf-8")
            report = root / ".cumcm" / "reports" / "innovation-freeze.json"
            report.write_text(
                '{"phase":"freeze","summary":{"passed":true},"tournament_sha256":"'
                + "0" * 64
                + '"}\n',
                encoding="utf-8",
            )
            config = workflow.load_config(root)
            config["artifacts"]["innovation_tournament"] = {
                "path": "strategy/innovation.json",
                "sha256": workflow.sha256(tournament),
            }
            config["artifacts"]["innovation_report"] = {
                "path": ".cumcm/reports/innovation-freeze.json",
                "sha256": workflow.sha256(report),
                "passed": True,
                "phase": "freeze",
            }
            workflow.save_config(root, config)
            with self.assertRaises(ValueError):
                workflow.approve_gate(
                    root,
                    "model_selection",
                    "队员甲",
                    "人工复核创新证据",
                    [str(evidence)],
                )


if __name__ == "__main__":
    unittest.main()
