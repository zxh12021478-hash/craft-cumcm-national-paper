from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def write_valid_strategy_contract(root: Path) -> dict:
    strategy_dir = root / "strategy"
    strategy_dir.mkdir(parents=True, exist_ok=True)
    reconciliation = {
        "version": 1,
        "bundle_sha256": "b" * 64,
        "reviewed_at": "2026-09-05T18:00:00+08:00",
        "reviewed_by": ["A", "B"],
        "artifacts": [
            {
                "path": "problem.pdf",
                "sha256": "c" * 64,
                "all_pages_or_sheets_reviewed": True,
                "equations_media_objects_reviewed": True,
                "headers_units_ranges_reviewed": True,
                "evidence": "A and B checked both rendered pages.",
            }
        ],
        "risk_closures": [],
        "subproblems": [
            {
                "id": "Q1",
                "prompt_locator": "problem page 2",
                "required_output": "report the minimum cost",
                "verified_by": "A",
            }
        ],
        "workbook_ranges": [],
        "unresolved_ambiguities": [],
    }
    reconciliation_path = strategy_dir / "reconciliation.json"
    reconciliation_path.write_text(json.dumps(reconciliation), encoding="utf-8")
    audit_report = {
        "root": str(root / "official"),
        "bundle_sha256": "b" * 64,
        "artifacts": [{"path": "problem.pdf", "type": ".pdf", "sha256": "c" * 64}],
        "risks_requiring_team_reconciliation": [],
        "reconciliation": str(reconciliation_path),
        "reconciliation_sha256": hashlib.sha256(reconciliation_path.read_bytes()).hexdigest(),
        "findings": [],
    }
    (strategy_dir / "audit.json").write_text(json.dumps(audit_report), encoding="utf-8")
    innovation = {
        "version": 1,
        "problem_id": "2026-A",
        "selection": {
            "shortlisted": ["I1", "I2", "I3"],
            "primary_candidate": "I1",
            "supporting_candidates": ["I2"],
        },
    }
    innovation_path = strategy_dir / "innovation.json"
    innovation_path.write_text(json.dumps(innovation), encoding="utf-8")
    innovation_audit = {
        "phase": "freeze",
        "problem_id": "2026-A",
        "tournament_sha256": hashlib.sha256(innovation_path.read_bytes()).hexdigest(),
        "summary": {"passed": True},
        "findings": [],
    }
    innovation_audit_path = strategy_dir / "innovation-audit.json"
    innovation_audit_path.write_text(json.dumps(innovation_audit), encoding="utf-8")
    return {
        "version": 1,
        "problem_id": "2026-A",
        "source_manifest": "strategy/audit.json",
        "source_reconciliation": {
            "audit_report": "strategy/audit.json",
            "reconciliation_record": "strategy/reconciliation.json",
        },
        "subproblems": [
            {
                "id": "Q1",
                "operative_question": "find the minimum feasible total cost",
                "dependencies": [],
                "inputs": [
                    {
                        "name": "demand",
                        "type": "vector",
                        "source": "problem.pdf",
                        "locator": "page 2 table 1",
                        "unit": "tonne",
                        "availability_timing": "known before allocation",
                    }
                ],
                "unknowns": ["minimum cost"],
                "decision_variables": ["x_i is allocated tonnes"],
                "method": "exact linear optimization with an enumerated check",
                "objectives": ["minimize total yuan cost"],
                "constraints": ["meet each demand without violating capacity"],
                "result_fields": [
                    {
                        "name": "Q1_MIN_COST",
                        "type": "scalar",
                        "unit": "yuan",
                        "machine_path": "results/q1.json#minimum_cost",
                        "paper_location": "section 5.1 table 3",
                        "acceptance": "feasible and equal to independent enumeration",
                    }
                ],
                "validation_ids": ["V-Q1-01"],
            }
        ],
        "workbook_range_mappings": [],
        "information_structure": {
            "decision_timeline": ["observe demand", "allocate supply", "settle cost"],
            "observation_timing": "all demand is observed before allocation",
            "uncertainty_semantics": "deterministic values from the official prompt",
            "multi_agent_semantics": "not applicable because one planner controls all allocations",
        },
        "innovation_contract": {
            "tournament_file": "strategy/innovation.json",
            "tournament_sha256": hashlib.sha256(innovation_path.read_bytes()).hexdigest(),
            "audit_report": "strategy/innovation-audit.json",
            "audit_report_sha256": hashlib.sha256(innovation_audit_path.read_bytes()).hexdigest(),
            "primary_candidate": "I1",
            "supporting_candidates": ["I2"],
        },
        "model_route": {
            "baseline": "complete enumeration over the small feasible set",
            "recommended": "linear optimization using the stated capacity structure",
            "structural_insight": "the constraint matrix permits a direct feasibility certificate",
        },
        "formulation": {
            "variables": ["x_i: allocated tonnes, x_i >= 0"],
            "parameters": ["d_i: demand in tonnes from the official prompt"],
            "objective": "minimize sum_i c_i x_i in yuan",
            "constraints": ["x_i >= d_i", "sum_i x_i <= capacity"],
            "data_transforms": ["convert all capacities to tonnes"],
            "solver": "deterministic linear solver with fixed tolerances",
            "fallback": "enumerate integer allocations and select the least-cost feasible point",
        },
        "validation": {
            "checks": ["recompute cost from saved allocation"],
            "acceptance_thresholds": ["maximum constraint violation <= 1e-8"],
            "failure_tests": ["reject the solution if any demand is unmet"],
        },
        "output_contract": {
            "entry_command": "python run_all.py",
            "machine_results": ["results/q1.json"],
            "verification_commands": ["python verifications/verify_q1.py"],
            "required_files": ["run_all.py", "results/q1.json", "verifications/verify_q1.py"],
        },
        "locked_decisions": ["objective", "constraints", "information timing", "validation threshold"],
        "open_decisions": [],
    }


class ContractTests(unittest.TestCase):
    def test_json_templates_match_schemas(self):
        from jsonschema import Draft202012Validator, FormatChecker

        pairs = [
            ("核心结果台账模板.json", "result-ledger.schema.json"),
            ("参考文献核验清单模板.json", "citation-manifest.schema.json"),
            ("干净运行清单模板.json", "execution-manifest.schema.json"),
            ("项目状态模板.json", "project-state.schema.json"),
            ("外部基线交接清单模板.json", "external-baseline-handoff.schema.json"),
            ("页面人工复核记录模板.json", "page-visual-qa.schema.json"),
            ("AI工具使用详情内部清单模板.json", "ai-use-manifest.schema.json"),
            ("求解策略合同模板.json", "strategy-contract.schema.json"),
            ("题面核对签字模板.json", "problem-reconciliation.schema.json"),
            ("结构洞察淘汰赛模板.json", "innovation-tournament.schema.json"),
            ("创新盲测校准台账模板.json", "innovation-calibration-ledger.schema.json"),
            ("能力盲测评估台账模板.json", "capability-benchmark-ledger.schema.json"),
        ]
        for template, schema in pairs:
            with self.subTest(template=template):
                instance = json.loads((ROOT / "assets" / "templates" / template).read_text(encoding="utf-8"))
                contract = json.loads((ROOT / "assets" / "schemas" / schema).read_text(encoding="utf-8"))
                self.assertEqual(
                    [],
                    list(Draft202012Validator(contract, format_checker=FormatChecker()).iter_errors(instance)),
                )


class SchedulerTests(unittest.TestCase):
    def test_takeover_deadline_and_freezes(self):
        scheduler = load_module("competition_scheduler")
        start = datetime.fromisoformat("2026-09-05T09:00:00+08:00")
        end = datetime.fromisoformat("2026-09-08T18:00:00+08:00")
        report = scheduler.schedule(start, end, "takeover")
        self.assertEqual(8, len(report["phases"]))
        self.assertEqual(report["phases"][-1]["hard_stop"], end.isoformat(timespec="minutes"))
        total = sum(row["allocated_hours"] for row in report["phases"])
        self.assertAlmostEqual(report["available_hours"], total, places=1)
        self.assertEqual(report["global_freezes"]["result_freeze"], report["phases"][4]["hard_stop"])


class ProblemStrategyTests(unittest.TestCase):
    def test_complete_strategy_contract_passes_semantic_gate(self):
        strategy_validator = load_module("validate_strategy_contract")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract = write_valid_strategy_contract(root)
            path = root / "strategy" / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            report = strategy_validator.inspect(path, root, True)
            self.assertEqual([], report["findings"])

    def test_strategy_rejects_innovation_selection_drift(self):
        strategy_validator = load_module("validate_strategy_contract")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract = write_valid_strategy_contract(root)
            contract["innovation_contract"]["primary_candidate"] = "I3"
            path = root / "strategy" / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            report = strategy_validator.inspect(path, root, True)
            self.assertIn(
                "INNOVATION_SELECTION_MISMATCH",
                {item["code"] for item in report["findings"]},
            )

    def test_problem_audit_strict_requires_bound_reconciliation(self):
        audit = load_module("audit_problem_bundle")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "problem.txt").write_text("问题一：给出最优值。\n", encoding="utf-8")
            report = audit.inspect(root)
            findings = audit.validate_reconciliation(report, None)
            self.assertIn("PROBLEM_RECONCILIATION_REQUIRED", {item["code"] for item in findings})
            record = {
                "version": 1,
                "bundle_sha256": report["bundle_sha256"],
                "reviewed_at": "2026-09-01T12:00:00+08:00",
                "reviewed_by": ["A"],
                "artifacts": [
                    {
                        "path": item["path"],
                        "sha256": item["sha256"],
                        "all_pages_or_sheets_reviewed": True,
                        "equations_media_objects_reviewed": True,
                        "headers_units_ranges_reviewed": True,
                        "evidence": "A checked the complete file.",
                    }
                    for item in report["artifacts"]
                ],
                "risk_closures": [],
                "subproblems": [
                    {
                        "id": "Q1",
                        "prompt_locator": "problem.txt line 1",
                        "required_output": "one optimal value",
                        "verified_by": "A",
                    }
                ],
                "workbook_ranges": [],
                "unresolved_ambiguities": [],
            }
            path = root / "reconciliation.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual([], audit.validate_reconciliation(report, path))

    def test_strategy_requires_exact_subproblem_and_workbook_coverage(self):
        strategy_validator = load_module("validate_strategy_contract")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = {
                "bundle_sha256": "a" * 64,
                "subproblems": [
                    {"id": "Q1", "required_output": "write values into the attachment workbook"},
                    {"id": "Q2", "required_output": "explain the policy"},
                ],
                "workbook_ranges": [
                    {
                        "file": "attachment.xlsx",
                        "sheet": "Data",
                        "range": "Data!G3:K34",
                        "role": "required_output",
                        "fields": ["decision values"],
                        "units": ["dimensionless"],
                        "used_by_subproblems": ["Q1"],
                        "verified_by": "A",
                        "evidence": "checked against the highlighted output region",
                    }
                ],
            }
            record_path = root / "reconciliation.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            audit_report = {
                "bundle_sha256": "a" * 64,
                "reconciliation": str(record_path),
                "reconciliation_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
                "artifacts": [{"path": "attachment.xlsx", "type": ".xlsx"}],
                "findings": [],
            }
            audit_path = root / "audit.json"
            audit_path.write_text(json.dumps(audit_report), encoding="utf-8")
            contract = json.loads((ROOT / "assets" / "templates" / "求解策略合同模板.json").read_text(encoding="utf-8"))
            contract["source_manifest"] = "audit.json"
            contract["source_reconciliation"] = {
                "audit_report": "audit.json",
                "reconciliation_record": "reconciliation.json",
            }
            contract["subproblems"] = [
                {
                    "id": "Q1",
                    "operative_question": "compute the approved optimal value",
                    "dependencies": [],
                    "inputs": [
                        {
                            "name": "data",
                            "type": "table",
                            "source": "attachment.xlsx",
                            "locator": "Data!A1:B10",
                            "unit": "dimensionless",
                            "availability_timing": "known before decision",
                        }
                    ],
                    "unknowns": ["optimal value"],
                    "decision_variables": ["x >= 0"],
                    "method": "enumerated exact optimization",
                    "objectives": ["minimize total cost"],
                    "constraints": ["all demand is met"],
                    "result_fields": [
                        {
                            "name": "Q1_VALUE",
                            "type": "scalar",
                            "unit": "yuan",
                            "machine_path": "results/q1.json#value",
                            "paper_location": "section 5",
                            "acceptance": "feasible and independently recomputed",
                        }
                    ],
                    "validation_ids": ["V1"],
                }
            ]
            contract["workbook_range_mappings"] = []
            contract["output_contract"]["machine_results"] = ["results/q1.json"]
            contract["open_decisions"] = []
            contract_path = root / "strategy.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            report = strategy_validator.inspect(contract_path, root, True)
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("SUBPROBLEM_COVERAGE_MISMATCH", codes)
            self.assertIn("WORKBOOK_MAPPING_MISSING", codes)
            self.assertIn("WORKBOOK_RANGE_COVERAGE_MISMATCH", codes)


class StateMachineTests(unittest.TestCase):
    def test_external_handoff_is_a_team_gate(self):
        state_manager = load_module("manage_project_state")
        state = json.loads((ROOT / "assets" / "templates" / "项目状态模板.json").read_text(encoding="utf-8"))
        for stage in state_manager.STAGES[:6]:
            state["stages"][stage]["status"] = "approved" if stage in state_manager.TEAM_GATES else "completed"
        args = Namespace(evidence=None, by=None, rationale=None, reason=None)
        state_manager.mutate(state, "start", "external_baseline_handoff", args)
        args.evidence = ["handoff manifest"]
        state_manager.mutate(state, "complete", "external_baseline_handoff", args)
        self.assertEqual("awaiting_team", state["stages"]["external_baseline_handoff"]["status"])
        args.by = "全队"
        args.rationale = "仅允许进入审计，不接受结论"
        state_manager.mutate(state, "approve", "external_baseline_handoff", args)
        self.assertEqual("approved", state["stages"]["external_baseline_handoff"]["status"])
        self.assertEqual("implementation", state["current_stage"])

    def test_final_state_cannot_bypass_prior_stages(self):
        submission = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            state = json.loads((ROOT / "assets" / "templates" / "项目状态模板.json").read_text(encoding="utf-8"))
            state["stages"]["final_audit"]["status"] = "approved"
            path.write_text(json.dumps(state), encoding="utf-8")
            codes = {item["code"] for item in submission.project_state_check(path, True)["findings"]}
            self.assertIn("PROJECT_STAGES_INCOMPLETE", codes)


class LedgerTests(unittest.TestCase):
    def test_result_ledger_pass_and_mismatch(self):
        verifier = load_module("verify_result_ledger")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "results").mkdir()
            (root / "results" / "metrics.json").write_text('{"accuracy": 0.9123}\n', encoding="utf-8")
            (root / "paper.txt").write_text("测试集准确率为91.23%。\n", encoding="utf-8")
            ledger = {
                "version": 1,
                "frozen_at": "2026-09-08T10:00:00+08:00",
                "approved_by_team": True,
                "results": [
                    {
                        "id": "q1_accuracy",
                        "question": "问题一",
                        "label": "准确率",
                        "value": 0.9123,
                        "unit": "",
                        "decision_critical": True,
                        "absolute_tolerance": 0.00001,
                        "relative_tolerance": 0,
                        "source": {"file": "results/metrics.json", "format": "json", "key": "accuracy"},
                        "occurrences": [
                            {
                                "file": "paper.txt",
                                "regex": "准确率为([0-9.]+)%",
                                "scale": 0.01
                            }
                        ]
                    }
                ]
            }
            ledger_path = root / "ledger.json"
            ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
            report = verifier.inspect(
                ledger_path,
                root,
                ROOT / "assets" / "schemas" / "result-ledger.schema.json",
                True,
            )
            self.assertEqual([], report["findings"])
            (root / "paper.txt").write_text("测试集准确率为88.00%。\n", encoding="utf-8")
            report = verifier.inspect(
                ledger_path,
                root,
                ROOT / "assets" / "schemas" / "result-ledger.schema.json",
                True,
            )
            self.assertIn("ARTIFACT_MISMATCH", {item["code"] for item in report["findings"]})
            ledger["frozen_at"] = "not-a-timestamp"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            report = verifier.inspect(
                ledger_path,
                root,
                ROOT / "assets" / "schemas" / "result-ledger.schema.json",
                True,
            )
            self.assertIn("INVALID_FREEZE_TIMESTAMP", {item["code"] for item in report["findings"]})


class CitationTests(unittest.TestCase):
    def test_numeric_citation_ranges(self):
        citations = load_module("validate_citations")
        self.assertEqual({"1", "2", "3", "7", "9"}, citations.numeric_citations("依据[1-3,7，9]。"))

    def test_template_placeholders_are_blocked(self):
        citations = load_module("validate_citations")
        manifest = ROOT / "assets" / "templates" / "参考文献核验清单模板.json"
        report = citations.inspect(
            manifest,
            None,
            False,
            1,
            ROOT / "assets" / "schemas" / "citation-manifest.schema.json",
            "off",
        )
        self.assertIn("CITATION_PLACEHOLDER", {item["code"] for item in report["findings"]})


class HandoffTests(unittest.TestCase):
    def test_approved_handoff_inventory(self):
        audit = load_module("audit_external_handoff")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ("handoff", "strategy", "baseline/code/results", "baseline/code/figures"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            strategy = root / "strategy" / "approved.md"
            strategy.write_text("# approved model contract\n", encoding="utf-8")
            contract = write_valid_strategy_contract(root)
            (root / "strategy" / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
            (root / "handoff" / "interactions.md").write_text("key interaction log\n", encoding="utf-8")
            (root / "baseline" / "paper.docx").write_bytes(b"inventory-only")
            (root / "baseline" / "code" / "run_all.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "baseline" / "code" / "execution.json").write_text("{}\n", encoding="utf-8")
            (root / "baseline" / "code" / "results" / "metrics.json").write_text("{}\n", encoding="utf-8")
            (root / "baseline" / "code" / "figures" / "q1.png").write_bytes(b"png")
            (root / "baseline" / "code" / "requirements.txt").write_text("\n", encoding="utf-8")
            (root / "baseline" / "implemented-contract.json").write_text(json.dumps(contract), encoding="utf-8")
            (root / "baseline" / "strategy-comparison.json").write_text('{"differences":[]}\n', encoding="utf-8")
            payload = {
                "version": 1,
                "generated_by": {
                    "tool": "ExternalTool",
                    "model_version": "v1",
                    "provider": "Provider",
                    "generated_at": "2026-09-06T08:00:00+08:00",
                    "interaction_log": "handoff/interactions.md"
                },
                "approved_strategy": {
                    "file": "strategy/approved.md",
                    "contract_file": "strategy/contract.json",
                    "sha256": hashlib.sha256(strategy.read_bytes()).hexdigest(),
                    "approved_by": ["A", "B", "C"],
                    "approved_at": "2026-09-05T20:00:00+08:00"
                },
                "artifacts": {
                    "paper": "baseline/paper.docx",
                    "code_root": "baseline/code",
                    "execution_manifest": "baseline/code/execution.json",
                    "implemented_strategy_contract": "baseline/implemented-contract.json",
                    "result_files": ["baseline/code/results/metrics.json"],
                    "figure_files": ["baseline/code/figures/q1.png"],
                    "dependency_file": "baseline/code/requirements.txt"
                },
                "strategy_comparison": {
                    "report": "baseline/strategy-comparison.json",
                    "reviewed_by": ["A"],
                    "reviewed_at": "2026-09-06T08:30:00+08:00",
                    "differences": []
                },
                "declared_scope": {
                    "followed_approved_strategy": True,
                    "core_model_changed": False,
                    "changes": []
                },
                "known_failures": [],
                "team_screening": {
                    "decision": "accepted_for_audit",
                    "screened_by": ["A"],
                    "screened_at": "2026-09-06T09:00:00+08:00",
                    "notes": "audit only"
                }
            }
            manifest = root / "handoff.json"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            report = audit.inspect(
                manifest,
                root,
                ROOT / "assets" / "schemas" / "external-baseline-handoff.schema.json",
            )
            self.assertEqual([], report["findings"])
            changed = dict(contract)
            changed["formulation"] = dict(contract["formulation"])
            changed["formulation"]["objective"] = "silently changed objective"
            (root / "baseline" / "implemented-contract.json").write_text(json.dumps(changed), encoding="utf-8")
            report = audit.inspect(
                manifest,
                root,
                ROOT / "assets" / "schemas" / "external-baseline-handoff.schema.json",
            )
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("UNDECLARED_STRATEGY_DIFFERENCE", codes)
            self.assertIn("FALSE_NO_CORE_CHANGE_DECLARATION", codes)


class VisualQATests(unittest.TestCase):
    def test_visual_record_is_bound_to_current_paper(self):
        submission = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "paper.docx"
            paper.write_bytes(b"current-paper")
            current_hash = hashlib.sha256(paper.read_bytes()).hexdigest()
            (root / "render.json").write_text(
                json.dumps({"metrics": {"source_sha256": current_hash}, "findings": []}),
                encoding="utf-8",
            )
            payload = {
                "version": 1,
                "paper_sha256": current_hash,
                "render_report": "render.json",
                "reviewed_by": ["A"],
                "reviewed_at": "2026-09-08T12:00:00+08:00",
                "all_pages_reviewed": True,
                "checks": {
                    "clipping": "pass",
                    "overlap": "pass",
                    "equations": "pass",
                    "tables": "pass",
                    "figures": "pass",
                    "captions": "pass",
                    "page_breaks": "pass",
                    "anonymity": "pass"
                },
                "open_issues": []
            }
            record = root / "qa.json"
            record.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual([], submission.visual_qa_check(record, paper)["findings"])
            paper.write_bytes(b"changed-paper")
            codes = {item["code"] for item in submission.visual_qa_check(record, paper)["findings"]}
            self.assertIn("VISUAL_QA_STALE", codes)
            reviewer_codes = {
                item["code"]
                for item in submission.visual_qa_check(record, paper, {"B", "C"})["findings"]
            }
            self.assertIn("VISUAL_QA_REVIEWER", reviewer_codes)


class ExecutionTests(unittest.TestCase):
    def test_clean_execution_and_independent_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "verifications").mkdir()
            (root / "approved_spec.json").write_text('{"expected":42}\n', encoding="utf-8")
            (root / "run_all.py").write_text(
                "from pathlib import Path\n"
                "Path('results').mkdir(exist_ok=True)\n"
                "Path('results/metrics.json').write_text('{\"value\": 42}\\n')\n",
                encoding="utf-8",
            )
            (root / "verifications" / "verify_result.py").write_text(
                "import json\n"
                "from pathlib import Path\n"
                "x=json.loads(Path('results/metrics.json').read_text())\n"
                "print('RESULT: PASS' if x['value']==42 else 'RESULT: FAIL')\n",
                encoding="utf-8",
            )
            manifest = {
                "version": 1,
                "entry": "run_all.py",
                "command_argv": ["{python}", "run_all.py"],
                "dependency_file": None,
                "dependency_lock": None,
                "python_environment": "system",
                "timeout_seconds": 60,
                "random_seeds": {"python": 2026},
                "expected_outputs": ["results/metrics.json"],
                "result_ledger": None,
                "verifications": [
                    {
                        "id": "independent_result",
                        "verification_type": "independent_implementation",
                        "independent_basis": "A separate script loads the saved result and checks the known fixture invariant.",
                        "inputs": ["results/metrics.json", "approved_spec.json"],
                        "expected_relation": "value == 42",
                        "reviewed_by": "A",
                        "command_argv": ["{python}", "verifications/verify_result.py"],
                        "required": True,
                        "pass_regex": "(?m)^RESULT:\\s*PASS\\s*$",
                        "fail_regex": "(?m)^RESULT:\\s*FAIL\\s*$",
                        "timeout_seconds": 30
                    }
                ]
            }
            manifest_path = root / "execution.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "execute_submission.py"),
                    str(root),
                    "--manifest",
                    str(manifest_path),
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            report = json.loads(proc.stdout)
            self.assertTrue(report["verifications"][0]["passed"])
            self.assertIn("results/metrics.json", report["created_files"])

    def test_preexisting_outputs_and_optional_failed_verifier_do_not_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "results").mkdir()
            (root / "verifications").mkdir()
            (root / "results" / "metrics.json").write_text('{"value": 42}\n', encoding="utf-8")
            (root / "main.py").write_text("print('did not generate outputs')\n", encoding="utf-8")
            (root / "verifications" / "verify.py").write_text("print('RESULT: FAIL')\n", encoding="utf-8")
            manifest = {
                "version": 1,
                "entry": "main.py",
                "command_argv": ["{python}", "main.py"],
                "python_environment": "system",
                "expected_outputs": ["results/metrics.json"],
                "verifications": [
                    {
                        "id": "optional",
                        "verification_type": "recomputation",
                        "independent_basis": "This deliberately invalid verifier only rereads a stale artifact.",
                        "inputs": ["results/metrics.json"],
                        "expected_relation": "value == 42",
                        "reviewed_by": "A",
                        "command_argv": ["{python}", "verifications/verify.py"],
                        "required": False,
                        "pass_regex": "RESULT: PASS"
                    }
                ]
            }
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "execute_submission.py"), str(root), "--manifest", str(path), "--json"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertNotEqual(0, proc.returncode)
            codes = {item["code"] for item in json.loads(proc.stdout)["findings"]}
            self.assertIn("NO_REQUIRED_VERIFICATION", codes)
            self.assertIn("EXPECTED_NOT_REGENERATED", codes)


class ComprehensionTests(unittest.TestCase):
    def test_threshold_and_auditor_cannot_be_self_declared(self):
        audit = load_module("audit_team_comprehension")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.json"
            topics = audit.TOPICS
            members = [
                {
                    "name": name,
                    "scores": {topic: 0 for topic in topics},
                    "challenge_question": "q",
                    "answer_evidence": "a",
                    "audited_by": "ExternalGhost",
                }
                for name in ("A", "B", "C")
            ]
            path.write_text(json.dumps({"minimum_score": 0, "members": members}), encoding="utf-8")
            codes = {item["code"] for item in audit.inspect(path, 3)["findings"]}
            self.assertIn("MINIMUM_SCORE_OVERRIDE", codes)
            self.assertIn("CROSS_AUDIT", codes)
            self.assertIn("MEMBER_UNDERSTANDING", codes)


class AIDeclarationTests(unittest.TestCase):
    def test_exact_no_ai_sentence_is_not_self_contradictory(self):
        submission = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as temp:
            paper = Path(temp) / "paper.txt"
            paper.write_text(
                "AI工具使用声明\n本参赛队在竞赛过程中未使用任何AI工具。\n参考文献\n[1] 示例",
                encoding="utf-8",
            )
            report = submission.ai_cross_check(paper, None, "no", True)
            self.assertEqual([], report["findings"])


class BenchmarkTests(unittest.TestCase):
    def test_benchmark_selection_is_reproducible(self):
        benchmark = load_module("run_benchmark_suite")
        catalog = ROOT / "assets" / "benchmarks" / "cumcm-historical-cases.json"
        left = benchmark.select(catalog, 3, 2026, False, 1)
        right = benchmark.select(catalog, 3, 2026, False, 1)
        self.assertEqual(
            [case["id"] for case in left["cases"]],
            [case["id"] for case in right["cases"]],
        )
        self.assertFalse(left["solution_blind"])
        self.assertEqual("unverified_until_case_ledger_audit", left["solution_blind_status"])
        self.assertTrue(
            all(case["isolation_requirements"]["unblind_only_after_sha256_freeze"] for case in left["cases"])
        )

    def test_benchmark_isolation_detects_contamination_and_hash_mismatch(self):
        benchmark_audit = load_module("audit_benchmark_isolation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            strategy = root / "strategy.md"
            strategy.write_text("frozen strategy\n", encoding="utf-8")
            digest = hashlib.sha256(strategy.read_bytes()).hexdigest()
            clean = {
                "version": 1,
                "benchmark_id": "cumcm-2099-A",
                "evaluation_mode": "retrospective_historical",
                "case_id": "2099A",
                "prior_model_memory": "none_declared",
                "pre_freeze_resources": [
                    {
                        "locator": "https://www.mcm.edu.cn/problem",
                        "category": "official_problem",
                        "case_scope": ["2099A"],
                    }
                ],
                "frozen_artifacts": [{"path": "strategy.md", "sha256": digest}],
                "frozen_at": "2099-09-01T00:00:00Z",
                "unblinded_at": None,
                "declared_solution_blind": False,
            }
            clean_report = benchmark_audit.inspect(clean, root)
            self.assertEqual("solution_isolated_historical_candidate", clean_report["evidence_label"])
            self.assertFalse(any(item["severity"] == "Blocker" for item in clean_report["findings"]))

            contaminated = json.loads(json.dumps(clean))
            contaminated["pre_freeze_resources"].append(
                {
                    "locator": "/skill/references/official-sample-casebook.md",
                    "category": "official_sample_casebook",
                    "case_scope": ["all"],
                }
            )
            contaminated["declared_solution_blind"] = True
            contaminated["frozen_artifacts"][0]["sha256"] = "0" * 64
            report = benchmark_audit.inspect(contaminated, root)
            codes = {item["code"] for item in report["findings"]}
            self.assertEqual("retrospective_rehearsal", report["evidence_label"])
            self.assertIn("BENCHMARK_CONTAMINATED", codes)
            self.assertIn("FROZEN_HASH_MISMATCH", codes)
            self.assertIn("SOLUTION_BLIND_CONTRADICTION", codes)


class OfficialSampleIndexTests(unittest.TestCase):
    def test_nested_year_index_is_discovered_and_papers_are_merged(self):
        samples = load_module("update_official_samples")
        landing = """
        <a href="2023gjsbqgdxssxjmjslwzs.shtml">2023 paper index</a>
        <a href="https://example.com/2023-other.shtml">external</a>
        """
        pages = samples.extract_index_pages(
            landing,
            "https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/2023qgdxssxjmjslwzs/",
            2023,
        )
        self.assertEqual(1, len(pages))
        page = """
        <a href="/zx/a/example.shtml">
        2023高教社杯全国大学生数学建模竞赛A题论文展示（A0127）
        </a>
        """
        papers = samples.extract_papers(page, pages[0], 2023)
        merged = samples.merge_papers([papers, papers])
        self.assertEqual(["A0127"], [paper["code"] for paper in merged])


if __name__ == "__main__":
    unittest.main()
