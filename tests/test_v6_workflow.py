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


class TruthHarnessTests(unittest.TestCase):
    def test_truth_template_matches_schema_and_passes(self):
        from jsonschema import Draft202012Validator

        payload = json.loads(
            (ROOT / "assets" / "templates" / "独立真值检查模板.json").read_text(encoding="utf-8")
        )
        schema = json.loads(
            (ROOT / "assets" / "schemas" / "truth-check-manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(payload)))
        report = load_module("truth_harness").inspect(payload, ROOT)
        self.assertEqual([], report["findings"])
        self.assertEqual(report["summary"]["total"], report["summary"]["passed"])

    def test_failed_truth_check_is_critical(self):
        payload = {
            "version": 1,
            "checks": [
                {
                    "id": "bad_constraint",
                    "family": "optimization",
                    "type": "constraint_set",
                    "tolerance": 1e-8,
                    "constraints": [{"name": "capacity", "lhs": 11, "sense": "<=", "rhs": 10}],
                }
            ],
        }
        report = load_module("truth_harness").inspect(payload, ROOT)
        self.assertIn("TRUTH_CHECK_FAILED", {item["code"] for item in report["findings"]})


class RenderStructureTests(unittest.TestCase):
    def test_toc_entries_do_not_impersonate_real_headings(self):
        renderer = load_module("render_and_check_pages")
        pages = [
            {"index": 1, "text": "摘要\n正文\n关键字：模型"},
            {"index": 2, "text": "目录\n一、问题重述 ........ 5\n二、问题分析 ........ 7\n模型建立 ........ 9"},
            {"index": 3, "text": "附录 B 完整代码 ........ 50\n参考文献 ........ 48"},
            {"index": 4, "text": "一、问题重述\n真实正文"},
            {"index": 5, "text": "附录\n程序代码"},
        ]
        self.assertEqual(4, renderer.first_heading_page(pages, r"问题重述", start=1))
        self.assertEqual(5, renderer.first_heading_page(pages, r"(^|\n)\s*附\s*录", start=1))
        self.assertEqual([2, 3], renderer.toc_pages(pages))


class CitationPeriodTests(unittest.TestCase):
    def test_live_competition_blocks_post_competition_reference(self):
        citations = load_module("validate_citations")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {
                "version": 1,
                "competition_context": {
                    "mode": "live_competition",
                    "competition_year": 2024,
                    "evidence_cutoff_date": "2024-09-08",
                },
                "citations": [
                    {
                        "id": "1",
                        "title": "A verified reference title",
                        "authors": ["A. Author"],
                        "year": 2025,
                        "source_type": "primary",
                        "doi": "10.1000/test-doi",
                        "verified_at": "2024-09-08",
                        "verified_by": "队员甲",
                        "verification_evidence": {
                            "source_snapshot_sha256": "1" * 64,
                            "bibliographic_locator": "publisher metadata record",
                            "claim_check": "The original method statement was reviewed by the team.",
                        },
                        "claims": [
                            {
                                "paper_location": "3.1",
                                "claim": "method definition",
                                "support_note": "The cited source defines the method.",
                            }
                        ],
                    }
                ],
            }
            manifest = root / "citations.json"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            report = citations.inspect(
                manifest,
                None,
                False,
                1,
                ROOT / "assets" / "schemas" / "citation-manifest.schema.json",
                "off",
            )
            self.assertIn("POST_COMPETITION_CITATION", {item["code"] for item in report["findings"]})


class UnifiedWorkflowTests(unittest.TestCase):
    def test_freeze_requires_two_human_gates_and_binds_hashes(self):
        workflow = load_module("cumcm_workflow")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow.init_project(root, "2026-A", None, "competition-lite")
            evidence = root / "strategy" / "evidence.md"
            evidence.write_text("team-reviewed evidence\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                workflow.approve_gate(root, "problem_reconciliation", "Codex", "reviewed", [str(evidence)])
            workflow.approve_gate(root, "problem_reconciliation", "队员甲", "逐页核对题面", [str(evidence)])
            with self.assertRaises(ValueError):
                workflow.freeze_strategy(root, [str(evidence)])
            tournament = root / "strategy" / "innovation.json"
            tournament.write_text('{"selection":{"primary_candidate":"I1"}}\n', encoding="utf-8")
            report = root / ".cumcm" / "reports" / "innovation-freeze.json"
            report.write_text(
                json.dumps(
                    {
                        "phase": "freeze",
                        "summary": {"passed": True},
                        "tournament_sha256": workflow.sha256(tournament),
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            config = workflow.load_config(root)
            config["artifacts"]["innovation_tournament"] = {
                "path": "strategy/innovation.json",
                "sha256": workflow.sha256(tournament),
                "kind": "file",
            }
            config["artifacts"]["innovation_report"] = {
                "path": ".cumcm/reports/innovation-freeze.json",
                "sha256": workflow.sha256(report),
                "passed": True,
                "phase": "freeze",
            }
            workflow.save_config(root, config)
            workflow.approve_gate(root, "model_selection", "队员乙", "比较三条路线后选定", [str(evidence)])
            frozen = workflow.freeze_strategy(root, [str(evidence)])
            self.assertEqual(hashlib.sha256(evidence.read_bytes()).hexdigest(), frozen["artifacts"][0]["sha256"])

    def test_result_acceptance_rejects_failed_reports(self):
        workflow = load_module("cumcm_workflow")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow.init_project(root, "2026-A", None, "competition-lite")
            evidence = root / "results" / "review.md"
            evidence.write_text("review\n", encoding="utf-8")
            config = workflow.load_config(root)
            config["artifacts"]["reproduction_report"] = {"path": "x", "passed": False}
            config["artifacts"]["truth_report"] = {"path": "y", "passed": True}
            workflow.save_config(root, config)
            with self.assertRaises(ValueError):
                workflow.approve_gate(root, "result_acceptance", "队员甲", "检查结果", [str(evidence)])

    def test_final_command_uses_unified_record_and_render_gate(self):
        workflow = load_module("cumcm_workflow")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow.init_project(root, "2026-A", None, "competition-lite")
            submission = root / "submission"
            workflow.register_artifact(root, "submission", str(submission))
            command, _ = workflow.validation_command(root, True)
            self.assertIn("--workflow-record", command)
            self.assertIn(str((root / ".cumcm" / "workflow.json").resolve()), command)
            self.assertIn("--render-dir", command)

    def test_unified_record_replaces_legacy_state_at_final_gate(self):
        validator = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {
                "version": 1,
                "profile": "final-strict",
                "gates": {},
                "artifacts": {
                    "reproduction_report": {"passed": True},
                    "truth_report": {"passed": True},
                },
                "declarations": {"ai_used": "yes", "external_baseline_used": "yes"},
            }
            for gate, reviewer in (
                ("problem_reconciliation", "队员甲"),
                ("model_selection", "队员乙"),
                ("baseline_deviation", "队员丙"),
                ("result_acceptance", "队员甲"),
            ):
                payload["gates"][gate] = {
                    "status": "approved",
                    "approved_at": "2026-09-07T12:00:00+08:00",
                    "approved_by": reviewer,
                    "rationale": "reviewed against evidence",
                    "evidence": ["evidence.md"],
                }
            path = root / "workflow.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            report = validator.workflow_record_check(path, True, {"队员甲", "队员乙", "队员丙"})
            self.assertEqual([], report["findings"])


if __name__ == "__main__":
    unittest.main()
