#!/usr/bin/env python3
"""Validate a solver-ready strategy contract and fail on unresolved governing choices."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def resolve_local(root: Path, relative, label: str, findings: list[dict]) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        findings.append(finding("Blocker", "STRATEGY_PATH", f"{label} must be a non-empty relative path."))
        return None
    try:
        path = (root / relative).resolve()
        path.relative_to(root.resolve())
    except Exception:
        findings.append(finding("Blocker", "STRATEGY_PATH", f"{label} escapes the strategy root.", relative))
        return None
    if not path.is_file():
        findings.append(finding("Critical", "STRATEGY_PATH", f"{label} does not exist.", relative))
        return None
    return path


def load_json(path: Path | None, label: str, findings: list[dict]) -> dict | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        findings.append(finding("Blocker", "STRATEGY_EVIDENCE_JSON", f"{label}: {exc}"))
        return None
    if not isinstance(payload, dict):
        findings.append(finding("Blocker", "STRATEGY_EVIDENCE_JSON", f"{label} root must be an object."))
        return None
    return payload


def inspect(path: Path, root: Path, solver_ready: bool) -> dict:
    findings = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"file": str(path), "findings": [finding("Blocker", "STRATEGY_JSON", str(exc))]}
    if not isinstance(payload, dict):
        return {"file": str(path), "findings": [finding("Blocker", "STRATEGY_SCHEMA", "Contract root must be an object.")]}
    schema_path = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "strategy-contract.schema.json"
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        findings.append(finding("Major", "JSONSCHEMA_UNAVAILABLE", "Strategy contract schema was not fully validated."))
    else:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
            key=lambda item: list(item.absolute_path),
        ):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            findings.append(finding("Blocker", "STRATEGY_SCHEMA", f"{location}: {error.message}"))
    blob = json.dumps(payload, ensure_ascii=False)
    if re.search(
        r"待验证|待团队|尚待|按真实赛题|变量名|参数名|写出量化|透明基线|团队批准的|"
        r"用可计算语言|题面输入|按题面|待估参数|逐列写明|给出量化阈值|主模型、透明基线",
        blob,
    ):
        findings.append(finding("Critical", "STRATEGY_PLACEHOLDER", "Strategy contract still contains template or unresolved wording."))
    open_decisions = payload.get("open_decisions", [])
    if solver_ready and open_decisions:
        findings.append(
            finding(
                "Blocker",
                "OPEN_GOVERNING_DECISIONS",
                "The contract cannot be labeled solver-ready while governing decisions remain open.",
                open_decisions,
            )
        )
    source_manifest_path = resolve_local(root, payload.get("source_manifest"), "source_manifest", findings)
    source_manifest = load_json(source_manifest_path, "source_manifest", findings)

    source_reconciliation = payload.get("source_reconciliation", {})
    if not isinstance(source_reconciliation, dict):
        source_reconciliation = {}
    audit_path = resolve_local(root, source_reconciliation.get("audit_report"), "source_reconciliation.audit_report", findings)
    record_path = resolve_local(
        root,
        source_reconciliation.get("reconciliation_record"),
        "source_reconciliation.reconciliation_record",
        findings,
    )
    audit_report = load_json(audit_path, "problem audit report", findings)
    reconciliation = load_json(record_path, "problem reconciliation record", findings)
    if source_manifest_path and audit_path and source_manifest_path != audit_path:
        findings.append(
            finding(
                "Blocker",
                "SOURCE_MANIFEST_MISMATCH",
                "source_manifest must be the same audited problem-bundle report named in source_reconciliation.",
            )
        )
    if audit_report:
        severe = [
            item
            for item in audit_report.get("findings", [])
            if isinstance(item, dict) and item.get("severity") in {"Blocker", "Critical", "Major"}
        ]
        if severe:
            findings.append(
                finding(
                    "Blocker",
                    "PROBLEM_AUDIT_NOT_APPROVED",
                    "The bound problem-bundle audit still has unresolved findings.",
                    severe,
                )
            )
    if audit_report and reconciliation:
        if audit_report.get("bundle_sha256") != reconciliation.get("bundle_sha256"):
            findings.append(
                finding(
                    "Blocker",
                    "PROBLEM_RECONCILIATION_MISMATCH",
                    "The problem reconciliation record is not bound to the strategy's audit report.",
                    {
                        "audit": audit_report.get("bundle_sha256"),
                        "record": reconciliation.get("bundle_sha256"),
                    },
                )
            )
        audit_record = audit_report.get("reconciliation")
        if audit_record and record_path and Path(audit_record).resolve() != record_path.resolve():
            findings.append(
                finding(
                    "Blocker",
                    "PROBLEM_RECONCILIATION_MISMATCH",
                    "The audit report was approved against a different reconciliation record.",
                    audit_record,
                )
            )
        if record_path:
            current_record_hash = hashlib.sha256(record_path.read_bytes()).hexdigest()
            if audit_report.get("reconciliation_sha256") != current_record_hash:
                findings.append(
                    finding(
                        "Blocker",
                        "PROBLEM_RECONCILIATION_STALE",
                        "The reconciliation record changed after the bound problem audit was produced.",
                        {
                            "audit": audit_report.get("reconciliation_sha256"),
                            "current": current_record_hash,
                        },
                    )
                )

    innovation_contract = payload.get("innovation_contract", {})
    if not isinstance(innovation_contract, dict):
        innovation_contract = {}
    tournament_path = resolve_local(
        root,
        innovation_contract.get("tournament_file"),
        "innovation_contract.tournament_file",
        findings,
    )
    innovation_audit_path = resolve_local(
        root,
        innovation_contract.get("audit_report"),
        "innovation_contract.audit_report",
        findings,
    )
    tournament = load_json(tournament_path, "innovation tournament", findings)
    innovation_audit = load_json(innovation_audit_path, "innovation audit report", findings)
    for label, bound_path, declared_hash in (
        ("innovation tournament", tournament_path, innovation_contract.get("tournament_sha256")),
        ("innovation audit report", innovation_audit_path, innovation_contract.get("audit_report_sha256")),
    ):
        if bound_path:
            actual_hash = hashlib.sha256(bound_path.read_bytes()).hexdigest()
            if not isinstance(declared_hash, str) or declared_hash == "0" * 64:
                findings.append(
                    finding(
                        "Blocker",
                        "INNOVATION_HASH_PLACEHOLDER",
                        f"The {label} hash must be captured after the artifact is frozen.",
                    )
                )
            elif declared_hash.lower() != actual_hash:
                findings.append(
                    finding(
                        "Blocker",
                        "INNOVATION_EVIDENCE_STALE",
                        f"The bound {label} changed after strategy approval.",
                        {"declared": declared_hash, "actual": actual_hash},
                    )
                )
    primary_candidate = innovation_contract.get("primary_candidate")
    supporting_candidates = innovation_contract.get("supporting_candidates", [])
    if tournament:
        selection = tournament.get("selection", {})
        if tournament.get("problem_id") != payload.get("problem_id"):
            findings.append(
                finding(
                    "Blocker",
                    "INNOVATION_PROBLEM_MISMATCH",
                    "The innovation tournament is for a different problem.",
                    {
                        "strategy": payload.get("problem_id"),
                        "tournament": tournament.get("problem_id"),
                    },
                )
            )
        if (
            selection.get("primary_candidate") != primary_candidate
            or selection.get("supporting_candidates", []) != supporting_candidates
        ):
            findings.append(
                finding(
                    "Blocker",
                    "INNOVATION_SELECTION_MISMATCH",
                    "The strategy contract changes the human-approved tournament selection.",
                    {
                        "contract": {
                            "primary": primary_candidate,
                            "supporting": supporting_candidates,
                        },
                        "tournament": {
                            "primary": selection.get("primary_candidate"),
                            "supporting": selection.get("supporting_candidates", []),
                        },
                    },
                )
            )
    if innovation_audit:
        if innovation_audit.get("problem_id") not in {None, payload.get("problem_id")}:
            findings.append(
                finding(
                    "Blocker",
                    "INNOVATION_AUDIT_PROBLEM_MISMATCH",
                    "The innovation audit report is for a different problem.",
                )
            )
        summary = innovation_audit.get("summary", {})
        if innovation_audit.get("phase") != "freeze" or summary.get("passed") is not True:
            findings.append(
                finding(
                    "Blocker",
                    "INNOVATION_AUDIT_NOT_APPROVED",
                    "The strategy must bind a passing freeze-phase innovation audit.",
                    {
                        "phase": innovation_audit.get("phase"),
                        "passed": summary.get("passed"),
                    },
                )
            )
        if tournament_path:
            actual_tournament_hash = hashlib.sha256(tournament_path.read_bytes()).hexdigest()
            if innovation_audit.get("tournament_sha256") != actual_tournament_hash:
                findings.append(
                    finding(
                        "Blocker",
                        "INNOVATION_AUDIT_TOURNAMENT_MISMATCH",
                        "The freeze audit is not bound to the tournament used by this strategy.",
                        {
                            "audit": innovation_audit.get("tournament_sha256"),
                            "current": actual_tournament_hash,
                        },
                    )
                )

    subproblems = payload.get("subproblems", [])
    if not isinstance(subproblems, list):
        subproblems = []
    subproblem_ids = [item.get("id") for item in subproblems if isinstance(item, dict)]
    if len(subproblem_ids) != len(set(subproblem_ids)):
        findings.append(finding("Blocker", "SUBPROBLEM_DUPLICATE", "Strategy subproblem IDs must be unique.", subproblem_ids))
    known_ids = set(subproblem_ids)
    result_names = []
    result_paths = []
    validation_ids = []
    for item in subproblems:
        if not isinstance(item, dict):
            continue
        subproblem_id = item.get("id")
        dependencies = item.get("dependencies", [])
        if isinstance(dependencies, list):
            invalid = sorted({value for value in dependencies if value not in known_ids or value == subproblem_id})
            if invalid:
                findings.append(
                    finding(
                        "Blocker",
                        "SUBPROBLEM_DEPENDENCY",
                        f"{subproblem_id} has missing or self-referential dependencies.",
                        invalid,
                    )
                )
        for result in item.get("result_fields", []) if isinstance(item.get("result_fields"), list) else []:
            if isinstance(result, dict):
                result_names.append(result.get("name"))
                result_paths.append(str(result.get("machine_path", "")).split("#", 1)[0])
        if isinstance(item.get("validation_ids"), list):
            validation_ids.extend(item["validation_ids"])
    if len(result_names) != len(set(result_names)):
        findings.append(finding("Blocker", "RESULT_FIELD_DUPLICATE", "Typed result-field names must be globally unique.", result_names))
    if len(validation_ids) != len(set(validation_ids)):
        findings.append(finding("Blocker", "VALIDATION_ID_DUPLICATE", "Validation IDs must be globally unique.", validation_ids))

    machine_results = payload.get("output_contract", {}).get("machine_results", [])
    machine_result_set = set(machine_results if isinstance(machine_results, list) else [])
    missing_machine_outputs = sorted({value for value in result_paths if value and value not in machine_result_set})
    if missing_machine_outputs:
        findings.append(
            finding(
                "Blocker",
                "RESULT_OUTPUT_UNDECLARED",
                "Every typed result field must live in an output_contract.machine_results file.",
                missing_machine_outputs,
            )
        )

    if reconciliation:
        reconciled_subproblems = [
            item.get("id")
            for item in reconciliation.get("subproblems", [])
            if isinstance(item, dict)
        ]
        if set(reconciled_subproblems) != known_ids or len(reconciled_subproblems) != len(subproblem_ids):
            findings.append(
                finding(
                    "Blocker",
                    "SUBPROBLEM_COVERAGE_MISMATCH",
                    "Strategy subproblems must exactly match the human-reconciled prompt subproblems.",
                    {
                        "strategy": subproblem_ids,
                        "reconciliation": reconciled_subproblems,
                    },
                )
            )

    mappings = payload.get("workbook_range_mappings", [])
    if not isinstance(mappings, list):
        mappings = []
    audited_workbooks = set()
    if audit_report:
        audited_workbooks = {
            item.get("path")
            for item in audit_report.get("artifacts", [])
            if isinstance(item, dict) and item.get("type") in {".xlsx", ".xlsm", ".xls"}
        }
    mapped_workbooks = {item.get("file") for item in mappings if isinstance(item, dict)}
    missing_workbooks = sorted(value for value in audited_workbooks if value not in mapped_workbooks)
    if missing_workbooks:
        findings.append(
            finding(
                "Blocker",
                "WORKBOOK_MAPPING_MISSING",
                "Every audited workbook must have explicit sheet/range/field/unit mappings.",
                missing_workbooks,
            )
        )
    unknown_workbooks = sorted(value for value in mapped_workbooks if value not in audited_workbooks)
    if unknown_workbooks:
        findings.append(
            finding(
                "Critical",
                "WORKBOOK_MAPPING_UNKNOWN",
                "Workbook mappings cite files outside the audited official bundle.",
                unknown_workbooks,
            )
        )
    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        invalid_users = sorted(set(mapping.get("used_by_subproblems", [])) - known_ids)
        if invalid_users:
            findings.append(
                finding(
                    "Blocker",
                    "WORKBOOK_MAPPING_SUBPROBLEM",
                    "Workbook mapping cites unknown subproblem IDs.",
                    invalid_users,
                )
            )
    mapping_fields = ("file", "sheet", "range", "role", "fields", "units", "used_by_subproblems")

    def mapping_key(item: dict) -> str:
        return json.dumps(
            {field: item.get(field) for field in mapping_fields},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    strategy_range_keys = {
        mapping_key(item)
        for item in mappings
        if isinstance(item, dict)
    }
    reconciled_ranges = (reconciliation or {}).get("workbook_ranges", [])
    if not isinstance(reconciled_ranges, list):
        reconciled_ranges = []
    reconciled_range_keys = {
        mapping_key(item)
        for item in reconciled_ranges
        if isinstance(item, dict)
    }
    if strategy_range_keys != reconciled_range_keys:
        findings.append(
            finding(
                "Blocker",
                "WORKBOOK_RANGE_COVERAGE_MISMATCH",
                "Strategy workbook mappings must exactly match the human-reconciled file/sheet/range/role/field/unit inventory.",
                {
                    "missing_from_strategy": [
                        json.loads(value) for value in sorted(reconciled_range_keys - strategy_range_keys)
                    ],
                    "not_in_reconciliation": [
                        json.loads(value) for value in sorted(strategy_range_keys - reconciled_range_keys)
                    ],
                },
            )
        )
    requested_outputs = " ".join(
        str(item.get("required_output", ""))
        for item in (reconciliation or {}).get("subproblems", [])
        if isinstance(item, dict)
    )
    if audited_workbooks and re.search(r"工作簿|附件|表格|单元格|填入|写入", requested_outputs):
        if not any(isinstance(item, dict) and item.get("role") == "required_output" for item in mappings):
            findings.append(
                finding(
                    "Blocker",
                    "WORKBOOK_OUTPUT_MAPPING_MISSING",
                    "The reconciled prompt requires workbook/table output, but no required_output range is mapped.",
                )
            )
    return {"file": str(path), "root": str(root), "solver_ready": solver_ready, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--solver-ready", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.contract.is_file():
        print(json.dumps({"error": "strategy contract not found"}, ensure_ascii=False))
        return 2
    report = inspect(args.contract.resolve(), (args.root or args.contract.parent).resolve(), args.solver_ready)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
