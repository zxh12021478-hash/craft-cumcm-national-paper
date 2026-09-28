#!/usr/bin/env python3
"""Orchestrate CUMCM static, runtime, cross-artifact, page, and compliance gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_json(
    script: Path,
    arguments: list[str],
    strict: bool = False,
    timeout: int = 2400,
) -> dict:
    command = [sys.executable, str(script), *arguments, "--json"]
    if strict:
        command.append("--strict")
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return {
            "command": command,
            "exit_code": 2,
            "findings": [finding("Blocker", "VALIDATOR_EXECUTION", str(exc))],
        }
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {
            "error": "validator returned non-JSON output",
            "stdout_tail": proc.stdout[-12000:],
            "stderr_tail": proc.stderr[-12000:],
        }
    payload["command"] = command
    payload["exit_code"] = proc.returncode
    if proc.returncode and not payload.get("findings"):
        payload["findings"] = [
            finding(
                "Blocker",
                "VALIDATOR_FAILURE",
                payload.get("error", "Validator failed without structured findings."),
            )
        ]
    return payload


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
        return "\n".join("".join(node.text or "" for node in p.iter(W + "t")) for p in root.iter(W + "p"))
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def discover(root: Path, names: tuple[str, ...]) -> Path | None:
    lowered = tuple(name.lower() for name in names)
    matches = [
        path
        for path in root.rglob("*")
        if path.is_file() and any(token in path.name.lower() for token in lowered)
    ]
    return sorted(matches, key=lambda path: (len(path.parts), str(path)))[0] if matches else None


def discover_paper(root: Path) -> Path | None:
    excluded = (
        "ai工具使用详情",
        "ai 工具使用详情",
        "支撑材料",
        "交接",
        "页面人工复核",
        "rendered-paper",
        "规则",
    )
    matches = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".docx", ".pdf"}
        and not any(token in path.name.lower() for token in excluded)
    ]
    if not matches:
        return None

    def rank(path: Path):
        text = str(path.relative_to(root)).lower()
        preferred = 0 if any(token in text for token in ("最终", "终稿", "final", "提交", "论文", "paper")) else 1
        baseline = 1 if any(token in text for token in ("baseline", "基线", "初稿")) else 0
        return preferred, baseline, len(path.parts), str(path)

    return sorted(matches, key=rank)[0]


def discover_ai_disclosure(root: Path) -> Path | None:
    matches = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".pdf", ".docx", ".md", ".txt"}
        and ("ai工具使用详情" in path.name.lower() or "ai 工具使用详情" in path.name.lower())
        and "内部清单" not in path.name
    ]
    return sorted(matches, key=lambda path: (0 if path.suffix.lower() == ".pdf" else 1, len(path.parts), str(path)))[0] if matches else None


def scoped_path(value: Path | None, root: Path) -> Path | None:
    if value is None:
        return None
    return (value if value.is_absolute() else root / value).resolve()


def project_state_check(path: Path, strict: bool) -> dict:
    findings = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        stages = payload.get("stages", {})
        if not isinstance(stages, dict):
            return {"file": str(path), "findings": [finding("Blocker", "PROJECT_STAGES_SCHEMA", "stages must be an object.")]}
        final_entry = stages.get("final_audit", {})
        final_status = final_entry.get("status") if isinstance(final_entry, dict) else None
        if strict and final_status != "approved":
            findings.append(
                finding(
                    "Blocker",
                    "FINAL_STATE_NOT_APPROVED",
                    "Final submission requires the team-approved final_audit stage.",
                    final_status,
                )
            )
        if strict:
            incomplete = {}
            malformed = {}
            for stage, entry in stages.items():
                if not isinstance(entry, dict):
                    malformed[stage] = type(entry).__name__
                    continue
                if entry.get("status") not in {"completed", "approved"}:
                    incomplete[stage] = entry.get("status")
                    continue
                if not entry.get("completed_at") or not entry.get("evidence"):
                    malformed[stage] = "missing completed_at or evidence"
                if entry.get("status") == "approved" and (
                    not entry.get("approved_at") or not entry.get("approved_by")
                ):
                    malformed[stage] = "approved without approver/timestamp"
            if payload.get("current_stage") != "complete":
                incomplete["current_stage"] = payload.get("current_stage")
            if incomplete:
                findings.append(
                    finding(
                        "Blocker",
                        "PROJECT_STAGES_INCOMPLETE",
                        "Final approval cannot bypass earlier workflow stages.",
                        incomplete,
                    )
                )
            if malformed:
                findings.append(
                    finding(
                        "Critical",
                        "PROJECT_STAGE_EVIDENCE",
                        "Completed/approved stages require evidence and timestamps.",
                        malformed,
                    )
                )
        decisions = payload.get("core_decisions", [])
        if not isinstance(decisions, list):
            findings.append(finding("Blocker", "CORE_DECISIONS_SCHEMA", "core_decisions must be an array."))
            decisions = []
        invalid_decisions = [index for index, item in enumerate(decisions) if not isinstance(item, dict)]
        if invalid_decisions:
            findings.append(
                finding("Blocker", "CORE_DECISIONS_SCHEMA", "Every core decision must be an object.", invalid_decisions)
            )
        unresolved = [
            item.get("id")
            for item in decisions
            if isinstance(item, dict) and item.get("state") in {"AI-proposed", "AI-recommended"}
        ]
        if unresolved:
            findings.append(
                finding(
                    "Blocker" if strict else "Critical",
                    "UNRESOLVED_CORE_DECISIONS",
                    "Core decisions remain only AI-proposed or AI-recommended.",
                    unresolved,
                )
            )
        return {"file": str(path), "current_stage": payload.get("current_stage"), "findings": findings}
    except Exception as exc:
        return {"file": str(path), "findings": [finding("Blocker", "PROJECT_STATE_READ", str(exc))]}


def workflow_record_check(
    path: Path,
    strict: bool,
    allowed_reviewers: set[str] | None = None,
) -> dict:
    findings = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"file": str(path), "findings": [finding("Blocker", "WORKFLOW_RECORD_READ", str(exc))]}
    gates = payload.get("gates")
    if payload.get("version") != 1 or not isinstance(gates, dict):
        return {
            "file": str(path),
            "findings": [finding("Blocker", "WORKFLOW_RECORD_SCHEMA", "Expected a version-1 workflow record with a gates object.")],
        }
    required = (
        "problem_reconciliation",
        "model_selection",
        "baseline_deviation",
        "result_acceptance",
    )
    if strict and payload.get("profile") != "final-strict":
        findings.append(
            finding(
                "Blocker",
                "WORKFLOW_PROFILE",
                "Final validation requires the workflow profile final-strict.",
                payload.get("profile"),
            )
        )
    for gate in required:
        entry = gates.get(gate)
        if not isinstance(entry, dict) or entry.get("status") != "approved":
            findings.append(finding("Blocker", "WORKFLOW_GATE", f"Required human gate is not approved: {gate}"))
            continue
        reviewer = str(entry.get("approved_by", "")).strip()
        if not reviewer or re.search(r"(?i)(?:\bai\b|\bgpt\b|\bcodex\b|assistant|模型|机器人)", reviewer):
            findings.append(
                finding("Blocker", "WORKFLOW_HUMAN_APPROVER", f"Gate {gate} lacks a valid human approver.", reviewer)
            )
        if allowed_reviewers is not None and reviewer not in allowed_reviewers:
            findings.append(
                finding(
                    "Blocker",
                    "WORKFLOW_APPROVER_NOT_AUDITED",
                    f"Gate {gate} was not approved by a member in the comprehension audit.",
                    {"reviewer": reviewer, "audited_team": sorted(allowed_reviewers)},
                )
            )
        if not entry.get("approved_at") or not entry.get("rationale") or not entry.get("evidence"):
            findings.append(
                finding(
                    "Critical",
                    "WORKFLOW_GATE_EVIDENCE",
                    f"Gate {gate} requires timestamp, rationale, and evidence.",
                )
            )
    artifacts = payload.get("artifacts", {})
    for report_name in ("reproduction_report", "truth_report"):
        report = artifacts.get(report_name) if isinstance(artifacts, dict) else None
        if strict and (not isinstance(report, dict) or not report.get("passed")):
            findings.append(
                finding("Blocker", "WORKFLOW_EVIDENCE_FAILED", f"Workflow report is absent or failed: {report_name}")
            )
    declarations = payload.get("declarations", {})
    for key in ("ai_used", "external_baseline_used"):
        if strict and declarations.get(key) not in {"yes", "no"}:
            findings.append(
                finding("Blocker", "WORKFLOW_DECLARATION_UNKNOWN", f"Workflow declaration is unresolved: {key}")
            )
    return {"file": str(path), "profile": payload.get("profile"), "findings": findings}


def ai_cross_check(paper: Path, disclosure: Path | None, ai_used: str, strict: bool) -> dict:
    findings = []
    try:
        text = extract_text(paper)
    except Exception as exc:
        return {"findings": [finding("Blocker", "AI_CROSS_CHECK_READ", str(exc))]}
    heading_pattern = r"AI\s*工具使用声明"
    no_ai_pattern = r"本参赛队在竞赛过程中未使用任何\s*AI\s*工具"
    used_ai_pattern = r"本参赛队在竞赛过程中使用了\s*AI\s*工具\s*[，,]\s*主要用于(?P<purpose>[\s\S]{1,200}?)\s*[，,]\s*详细使用情况见支撑材料"
    has_heading = bool(re.search(heading_pattern, text, re.I))
    has_no_ai = bool(re.search(no_ai_pattern, text, re.I))
    used_ai_match = re.search(used_ai_pattern, text, re.I)
    has_used_ai = bool(used_ai_match)

    def check_heading_and_position() -> None:
        if not has_heading:
            findings.append(finding("Blocker", "AI_DECLARATION_HEADING", "The 2026 rules require an AI工具使用声明 section."))
            return
        heading_index = re.search(heading_pattern, text, re.I).start()
        reference_matches = list(re.finditer(r"(?:^|\n)\s*参考文献\s*(?:\n|$)", text, re.I))
        if not reference_matches:
            findings.append(finding("Critical", "AI_DECLARATION_POSITION_UNVERIFIED", "Could not locate the references heading after the AI-use declaration."))
        elif heading_index > reference_matches[-1].start():
            findings.append(finding("Blocker", "AI_DECLARATION_POSITION", "The 2026 AI-use declaration must appear before the references."))

    if ai_used == "yes":
        if has_no_ai:
            findings.append(finding("Blocker", "AI_USE_CONTRADICTION", "Paper declares no AI use although AI use was specified."))
        if disclosure is None:
            findings.append(finding("Blocker", "NO_AI_DISCLOSURE", "AI use was specified, but no AI-use detail file was found."))
        if strict:
            check_heading_and_position()
            if not has_used_ai:
                findings.append(finding("Blocker", "AI_USE_DECLARATION_MISSING", "The official 2026 used-AI declaration wording was not recognized."))
            elif re.search(r"简要用途|如语言润色|代码调试等|[【\[]", used_ai_match.group("purpose")):
                findings.append(finding("Blocker", "AI_USE_DECLARATION_PLACEHOLDER", "Replace the bracketed example with the team's actual concise AI uses."))
    elif ai_used == "no":
        if disclosure is not None or has_used_ai:
            findings.append(finding("Blocker", "AI_USE_CONTRADICTION", "Artifacts indicate AI use although --ai-used no was specified."))
        if strict:
            check_heading_and_position()
            if not has_no_ai:
                findings.append(finding("Blocker", "NO_AI_DECLARATION", "The official 2026 no-AI declaration wording was not recognized."))
    elif strict:
        findings.append(finding("Blocker", "AI_USE_UNKNOWN", "Final validation requires --ai-used yes or --ai-used no."))
    return {
        "paper": str(paper),
        "disclosure": str(disclosure) if disclosure else None,
        "ai_used": ai_used,
        "findings": findings,
    }


def visual_qa_check(path: Path, paper: Path, allowed_reviewers: set[str] | None = None) -> dict:
    findings = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"file": str(path), "findings": [finding("Blocker", "VISUAL_QA_JSON", str(exc))]}
    declared = str(payload.get("paper_sha256", "")).lower()
    actual = sha256(paper)
    try:
        reviewed_at = datetime.fromisoformat(str(payload.get("reviewed_at", "")).replace("Z", "+00:00"))
        if reviewed_at.tzinfo is None or reviewed_at.utcoffset() is None:
            raise ValueError("timezone offset is required")
    except Exception as exc:
        findings.append(
            finding(
                "Blocker",
                "VISUAL_QA_TIMESTAMP",
                f"reviewed_at must be an ISO timestamp with timezone: {exc}",
                payload.get("reviewed_at"),
            )
        )
    reviewers = {str(value).strip() for value in payload.get("reviewed_by", []) if str(value).strip()}
    if allowed_reviewers is not None and (not reviewers or not reviewers <= allowed_reviewers):
        findings.append(
            finding(
                "Blocker",
                "VISUAL_QA_REVIEWER",
                "Page review must be signed by an audited team member.",
                {"reviewers": sorted(reviewers), "team": sorted(allowed_reviewers)},
            )
        )
    if declared == "0" * 64:
        findings.append(finding("Blocker", "VISUAL_QA_PLACEHOLDER", "The page-review record still contains the template paper hash."))
    elif declared != actual:
        findings.append(
            finding(
                "Blocker",
                "VISUAL_QA_STALE",
                "The page-review record does not belong to the current paper.",
                {"declared": declared, "actual": actual},
            )
        )
    raw_report = str(payload.get("render_report", "")).strip()
    try:
        render_report = (path.parent / raw_report).resolve()
        render_report.relative_to(path.parent.resolve())
        if not render_report.is_file():
            raise FileNotFoundError(raw_report)
        render_payload = json.loads(render_report.read_text(encoding="utf-8"))
        rendered_hash = str(render_payload.get("metrics", {}).get("source_sha256", "")).lower()
        if rendered_hash != actual:
            findings.append(
                finding(
                    "Blocker",
                    "VISUAL_QA_RENDER_STALE",
                    "The reviewed render report does not belong to the current paper.",
                    {"rendered": rendered_hash, "actual": actual},
                )
            )
        render_failures = [
            item
            for item in render_payload.get("findings", [])
            if item.get("severity") in {"Blocker", "Critical", "Major"}
        ]
        if render_failures:
            findings.append(
                finding(
                    "Critical",
                    "VISUAL_QA_RENDER_FINDINGS",
                    "The reviewed render report still contains unresolved findings.",
                    render_failures,
                )
            )
    except Exception as exc:
        findings.append(
            finding(
                "Critical",
                "VISUAL_QA_RENDER_REPORT",
                f"Could not validate the referenced render report: {exc}",
                raw_report,
            )
        )
    return {"file": str(path), "paper": str(paper), "findings": findings}


def external_ai_cross_check(handoff: Path, disclosure: Path | None) -> dict:
    findings = []
    if disclosure is None:
        return {
            "handoff": str(handoff),
            "findings": [finding("Blocker", "EXTERNAL_AI_UNDISCLOSED", "External AI baseline use requires an AI-use detail file.")],
        }
    try:
        payload = json.loads(handoff.read_text(encoding="utf-8"))
        tool = str(payload.get("generated_by", {}).get("tool", "")).strip()
        text = extract_text(disclosure)
        if tool and tool not in text:
            findings.append(
                finding(
                    "Blocker",
                    "EXTERNAL_TOOL_NOT_DISCLOSED",
                    "The external baseline generator was not recognized in the AI-use detail file.",
                    tool,
                )
            )
    except Exception as exc:
        findings.append(finding("Blocker", "EXTERNAL_DISCLOSURE_CROSS_CHECK", str(exc)))
    return {"handoff": str(handoff), "disclosure": str(disclosure), "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path, help="Submission directory")
    parser.add_argument("--paper", type=Path)
    parser.add_argument("--code", type=Path)
    parser.add_argument("--ai-disclosure", type=Path)
    parser.add_argument("--ai-use-manifest", type=Path)
    parser.add_argument("--ai-used", choices=("yes", "no", "unknown"), default="unknown")
    parser.add_argument("--result-ledger", type=Path)
    parser.add_argument("--citation-manifest", type=Path)
    parser.add_argument("--execution-manifest", type=Path)
    parser.add_argument("--project-state", type=Path)
    parser.add_argument("--workflow-record", type=Path)
    parser.add_argument("--team-audit", type=Path)
    parser.add_argument("--handoff-manifest", type=Path)
    parser.add_argument("--external-baseline-used", choices=("yes", "no", "unknown"), default="unknown")
    parser.add_argument("--visual-qa", type=Path)
    parser.add_argument("--rules-manifest", type=Path)
    parser.add_argument("--rules-snapshot", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--run-clean", action="store_true")
    parser.add_argument("--allow-dependency-install", action="store_true")
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--external-refchecker", choices=("off", "auto", "required"), default="off")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Run final-submission fail-closed gates")
    args = parser.parse_args()

    root = args.submission.resolve()
    if not root.is_dir():
        print(json.dumps({"error": "submission directory not found", "submission": str(root)}, ensure_ascii=False))
        return 2
    scripts = Path(__file__).resolve().parent
    skill_root = scripts.parent
    paper = scoped_path(args.paper, root) or discover_paper(root)
    code = scoped_path(args.code, root) or root
    disclosure = scoped_path(args.ai_disclosure, root) or discover_ai_disclosure(root)
    ai_use_manifest = scoped_path(args.ai_use_manifest, root) or discover(root, ("ai工具使用详情内部清单", "ai_use_manifest"))
    result_ledger = scoped_path(args.result_ledger, root) or discover(root, ("核心结果台账", "result_ledger"))
    citation_manifest = scoped_path(args.citation_manifest, root) or discover(root, ("参考文献核验清单", "citation_manifest"))
    execution_manifest = scoped_path(args.execution_manifest, root) or discover(root, ("干净运行清单", "execution_manifest"))
    project_state = scoped_path(args.project_state, root) or discover(root, ("项目状态", "project_state"))
    workflow_record = scoped_path(args.workflow_record, root) if args.workflow_record else None
    team_audit = scoped_path(args.team_audit, root) or discover(root, ("全员理解审计", "team_comprehension"))
    handoff_manifest = scoped_path(args.handoff_manifest, root) or discover(root, ("外部基线交接清单", "external_baseline_handoff"))
    visual_qa = scoped_path(args.visual_qa, root) or discover(root, ("页面人工复核记录", "page_visual_qa"))
    rules_manifest = args.rules_manifest or skill_root / "assets" / "rules" / "cumcm-current-rules.json"
    default_rules_snapshot = skill_root / "assets" / "rules" / "cumcm-current-rules.snapshot.json"
    rules_snapshot = args.rules_snapshot or (default_rules_snapshot if default_rules_snapshot.is_file() else None)

    report = {"submission": str(root), "strict": args.strict, "checks": {}}
    if args.strict:
        report["checks"]["environment_preflight"] = run_json(
            scripts / "preflight_environment.py",
            ["--profile", "final"],
            True,
        )
    elif args.run_clean:
        report["checks"]["environment_preflight"] = run_json(
            scripts / "preflight_environment.py",
            ["--profile", "takeover"],
            False,
        )
    if paper and paper.is_file():
        if paper.suffix.lower() == ".docx":
            report["checks"]["docx"] = run_json(scripts / "validate_docx.py", [str(paper)], args.strict)
        if args.render_dir:
            render_output = (args.render_dir if args.render_dir.is_absolute() else root / args.render_dir).resolve()
            report["checks"]["rendered_pages"] = run_json(
                scripts / "render_and_check_pages.py",
                [
                    str(paper),
                    "--output-dir",
                    str(render_output),
                    "--output",
                    str(render_output / "render-report.json"),
                ],
                args.strict,
            )
        elif args.strict:
            report["checks"]["rendered_pages"] = {
                "exit_code": 1,
                "findings": [finding("Blocker", "NO_RENDER_GATE", "Final validation requires --render-dir and manual inspection of the rendered page images.")],
            }
    else:
        report["checks"]["paper"] = {
            "exit_code": 1,
            "findings": [finding("Blocker" if args.strict else "Major", "NO_PAPER", "No DOCX or PDF paper was supplied or discovered.")],
        }

    audited_team_names = None
    if team_audit and team_audit.is_file():
        try:
            team_payload = json.loads(team_audit.read_text(encoding="utf-8"))
            audited_team_names = {
                str(member.get("name", "")).strip()
                for member in team_payload.get("members", [])
                if isinstance(member, dict) and str(member.get("name", "")).strip()
            }
        except Exception:
            audited_team_names = set()

    if paper and visual_qa:
        report["checks"]["visual_qa_contract"] = run_json(
            scripts / "validate_contract.py",
            [str(visual_qa), str(skill_root / "assets" / "schemas" / "page-visual-qa.schema.json")],
            args.strict,
        )
        report["checks"]["visual_qa_paper_match"] = visual_qa_check(
            visual_qa,
            paper,
            audited_team_names if args.strict else None,
        )
    elif args.strict:
        report["checks"]["visual_qa"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_VISUAL_QA", "Final validation requires a signed page-by-page visual QA record.")],
        }

    report["checks"]["code_static"] = run_json(scripts / "validate_code_bundle.py", [str(code)], args.strict)
    if execution_manifest:
        report["checks"]["execution_contract"] = run_json(
            scripts / "validate_contract.py",
            [str(execution_manifest), str(skill_root / "assets" / "schemas" / "execution-manifest.schema.json")],
            args.strict,
        )
        if args.run_clean:
            static_blockers = [
                item
                for item in report["checks"]["code_static"].get("findings", [])
                if item.get("severity") in {"Blocker", "Critical"}
            ]
            if static_blockers:
                report["checks"]["clean_execution"] = {
                    "exit_code": 1,
                    "findings": [
                        finding(
                            "Blocker",
                            "EXECUTION_BLOCKED_BY_STATIC_QA",
                            "Code was not executed because static QA found Blocker/Critical defects; external code is not sandboxed.",
                            static_blockers,
                        )
                    ],
                }
            else:
                execution_args = [str(code), "--manifest", str(execution_manifest)]
                if args.allow_dependency_install:
                    execution_args.append("--install-deps")
                report["checks"]["clean_execution"] = run_json(
                    scripts / "execute_submission.py",
                    execution_args,
                    False,
                    timeout=2700,
                )
    elif args.strict or args.run_clean:
        report["checks"]["execution_contract"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_EXECUTION_MANIFEST", "Clean execution requires an execution manifest.")],
        }
    if args.strict and not args.run_clean:
        report["checks"]["clean_execution"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "CLEAN_RUN_NOT_REQUESTED", "Final validation requires --run-clean.")],
        }

    if result_ledger:
        ledger_args = [str(result_ledger), "--root", str(root)]
        if args.strict:
            ledger_args.append("--final")
        report["checks"]["result_ledger"] = run_json(scripts / "verify_result_ledger.py", ledger_args, args.strict)
    elif args.strict:
        report["checks"]["result_ledger"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_RESULT_LEDGER", "Final validation requires a frozen canonical result ledger.")],
        }

    if citation_manifest:
        citation_args = [str(citation_manifest)]
        if paper:
            citation_args.extend(["--paper", str(paper)])
        if args.online or args.strict:
            citation_args.append("--online")
        citation_args.extend(["--external-refchecker", args.external_refchecker])
        report["checks"]["citations"] = run_json(scripts / "validate_citations.py", citation_args, args.strict, timeout=1800)
    elif args.strict:
        report["checks"]["citations"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_CITATION_MANIFEST", "Final validation requires a manually verified citation manifest.")],
        }

    if disclosure:
        disclosure_args = [str(disclosure)]
        if ai_use_manifest:
            disclosure_args.extend(["--manifest", str(ai_use_manifest)])
        if handoff_manifest and handoff_manifest.is_file():
            try:
                external_tool = str(
                    json.loads(handoff_manifest.read_text(encoding="utf-8"))
                    .get("generated_by", {})
                    .get("tool", "")
                ).strip()
                if external_tool:
                    disclosure_args.extend(["--expected-tool", external_tool])
            except Exception:
                pass
        report["checks"]["ai_disclosure"] = run_json(
            scripts / "validate_ai_disclosure.py",
            disclosure_args,
            args.strict,
        )
    if args.ai_used == "yes" and disclosure is None:
        report["checks"]["ai_disclosure"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_AI_DISCLOSURE", "Declared AI use requires an AI-use detail file.")],
        }
    elif args.ai_used == "no" and disclosure is not None:
        report["checks"]["ai_disclosure_declaration"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "AI_USE_CONTRADICTION", "An AI-use detail file exists although --ai-used no was declared.")],
        }
    if args.ai_used == "yes" and args.strict and ai_use_manifest is None:
        report["checks"]["ai_use_manifest"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_AI_USE_MANIFEST", "Final validation requires a structured internal AI-use manifest.")],
        }
    if args.ai_used == "no" and ai_use_manifest is not None:
        report["checks"]["ai_use_manifest"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "AI_USE_CONTRADICTION", "An AI-use manifest exists although --ai-used no was declared.")],
        }
    elif args.strict and args.ai_used == "unknown":
        report["checks"]["ai_use_declaration"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "AI_USE_UNKNOWN", "Final validation requires --ai-used yes or --ai-used no.")],
        }
    if paper:
        report["checks"]["ai_cross_artifact"] = ai_cross_check(paper, disclosure, args.ai_used, args.strict)

    if workflow_record:
        report["checks"]["workflow_record"] = workflow_record_check(
            workflow_record,
            args.strict,
            audited_team_names if args.strict else None,
        )
    elif project_state:
        report["checks"]["project_state_contract"] = run_json(
            scripts / "validate_contract.py",
            [str(project_state), str(skill_root / "assets" / "schemas" / "project-state.schema.json")],
            args.strict,
        )
        report["checks"]["project_state_gate"] = project_state_check(project_state, args.strict)
    elif args.strict:
        report["checks"]["workflow_gate"] = {
            "exit_code": 1,
            "findings": [
                finding(
                    "Blocker",
                    "NO_WORKFLOW_RECORD",
                    "Final validation requires either the unified workflow record or the legacy human-led project state.",
                )
            ],
        }

    if team_audit:
        report["checks"]["team_comprehension"] = run_json(
            scripts / "audit_team_comprehension.py",
            [str(team_audit)],
            args.strict,
        )
    elif args.strict:
        report["checks"]["team_comprehension"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_TEAM_AUDIT", "Final validation requires a cross-audited team comprehension record.")],
        }

    if handoff_manifest:
        report["checks"]["external_handoff"] = run_json(
            scripts / "audit_external_handoff.py",
            [str(handoff_manifest), "--root", str(root)],
            args.strict,
        )
        report["checks"]["external_ai_disclosure"] = external_ai_cross_check(handoff_manifest, disclosure)
    elif args.external_baseline_used == "yes":
        report["checks"]["external_handoff"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "NO_EXTERNAL_HANDOFF", "External baseline use was declared, but no handoff manifest was found.")],
        }
    if args.strict and args.external_baseline_used == "unknown":
        report["checks"]["external_baseline_declaration"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "EXTERNAL_BASELINE_UNKNOWN", "Final validation requires --external-baseline-used yes or no.")],
        }
    if args.external_baseline_used == "no" and handoff_manifest:
        report["checks"]["external_baseline_declaration"] = {
            "exit_code": 1,
            "findings": [finding("Blocker", "EXTERNAL_BASELINE_CONTRADICTION", "A handoff manifest exists although external baseline use was declared no.")],
        }

    if args.online or args.strict:
        rule_args = ["--manifest", str(rules_manifest)]
        if rules_snapshot:
            rule_args.extend(["--snapshot", str(rules_snapshot)])
        elif args.strict:
            report["checks"]["official_rule_snapshot"] = {
                "exit_code": 1,
                "findings": [finding("Major", "NO_RULE_SNAPSHOT", "Final validation should compare current official pages with a reviewed snapshot.")],
            }
        report["checks"]["official_rules"] = run_json(
            scripts / "check_official_rules.py",
            rule_args,
            args.strict,
            timeout=180,
        )

    severities = [
        item.get("severity")
        for check in report["checks"].values()
        for item in check.get("findings", [])
    ]
    blocking = {"Blocker", "Critical", "Major"} if args.strict else {"Blocker", "Critical"}
    report["summary"] = {
        "blockers": severities.count("Blocker"),
        "critical": severities.count("Critical"),
        "major": severities.count("Major"),
        "minor": severities.count("Minor"),
        "pass": not any(severity in blocking for severity in severities),
        "manual_visual_inspection_required": bool(args.render_dir) and not bool(visual_qa),
        "visual_qa_recorded": bool(visual_qa),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return int(not report["summary"]["pass"])


if __name__ == "__main__":
    raise SystemExit(main())
