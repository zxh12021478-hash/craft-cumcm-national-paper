#!/usr/bin/env python3
"""Validate and inventory an overnight external baseline without executing it."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path


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


def inside(root: Path, raw: str) -> Path:
    path = (root / raw).resolve()
    path.relative_to(root.resolve())
    return path


def schema_findings(payload: dict, schema: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Handoff manifest was not checked with JSON Schema.")]
    contract = json.loads(schema.read_text(encoding="utf-8"))
    output = []
    for error in sorted(Draft202012Validator(contract, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "HANDOFF_SCHEMA", f"{location}: {error.message}"))
    return output


def contract_findings(payload: dict, schema: Path, label: str) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", f"{label} was not checked with JSON Schema.")]
    contract = json.loads(schema.read_text(encoding="utf-8"))
    output = []
    for error in sorted(Draft202012Validator(contract, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "STRATEGY_CONTRACT_SCHEMA", f"{label} {location}: {error.message}"))
    return output


def semantic_contract_findings(path: Path, root: Path, label: str) -> list[dict]:
    validator_path = Path(__file__).resolve().parent / "validate_strategy_contract.py"
    spec = importlib.util.spec_from_file_location("_cumcm_strategy_validator", validator_path)
    if spec is None or spec.loader is None:
        return [finding("Blocker", "STRATEGY_VALIDATOR_LOAD", f"{label}: could not load semantic strategy validator.")]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        report = module.inspect(path, root, True)
    except Exception as exc:
        return [finding("Blocker", "STRATEGY_VALIDATOR_CRASH", f"{label}: {exc}")]
    output = []
    for item in report.get("findings", []):
        copied = dict(item)
        copied["message"] = f"{label}: {copied.get('message', '')}"
        output.append(copied)
    return output


def nested(payload: dict, dotted: str):
    current = payload
    for part in dotted.split("."):
        current = current[part]
    return current


def inspect(manifest_path: Path, root: Path, schema: Path) -> dict:
    findings: list[dict] = []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"manifest": str(manifest_path), "findings": [finding("Blocker", "HANDOFF_JSON", str(exc))]}
    if not isinstance(payload, dict):
        return {"manifest": str(manifest_path), "findings": [finding("Blocker", "HANDOFF_SCHEMA", "Manifest root must be an object.")]}
    findings.extend(schema_findings(payload, schema))
    generated_by = payload.get("generated_by") if isinstance(payload.get("generated_by"), dict) else {}
    approved_strategy = payload.get("approved_strategy") if isinstance(payload.get("approved_strategy"), dict) else {}
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    comparison = payload.get("strategy_comparison") if isinstance(payload.get("strategy_comparison"), dict) else {}
    inventory = {}
    path_fields = {
        "interaction_log": generated_by.get("interaction_log"),
        "approved_strategy": approved_strategy.get("file"),
        "approved_strategy_contract": approved_strategy.get("contract_file"),
        "paper": artifacts.get("paper"),
        "code_root": artifacts.get("code_root"),
        "execution_manifest": artifacts.get("execution_manifest"),
        "implemented_strategy_contract": artifacts.get("implemented_strategy_contract"),
        "strategy_comparison_report": comparison.get("report"),
        "dependency_file": artifacts.get("dependency_file"),
    }
    for index, value in enumerate(artifacts.get("result_files", []) if isinstance(artifacts.get("result_files"), list) else []):
        path_fields[f"result_files[{index}]"] = value
    for index, value in enumerate(artifacts.get("figure_files", []) if isinstance(artifacts.get("figure_files"), list) else []):
        path_fields[f"figure_files[{index}]"] = value
    for label, raw in path_fields.items():
        if not raw:
            if label == "dependency_file":
                continue
            findings.append(finding("Critical", "HANDOFF_PATH", f"{label}: no path was declared."))
            continue
        try:
            path = inside(root, raw)
            if not path.exists():
                raise FileNotFoundError(raw)
            record = {"path": str(path), "kind": "directory" if path.is_dir() else "file"}
            if path.is_file():
                record.update(bytes=path.stat().st_size, sha256=sha256(path))
            inventory[label] = record
        except Exception as exc:
            findings.append(finding("Critical", "HANDOFF_PATH", f"{label}: {exc}", raw))
    strategy = inventory.get("approved_strategy")
    declared_hash = str(approved_strategy.get("sha256", "")).lower()
    if declared_hash == "0" * 64:
        findings.append(
            finding(
                "Blocker",
                "STRATEGY_HASH_PLACEHOLDER",
                "The strategy hash is still the template placeholder; hash the approved strategy before handoff.",
            )
        )
    if strategy and strategy.get("sha256") != declared_hash:
        findings.append(
            finding(
                "Blocker",
                "STRATEGY_HASH",
                "The approved strategy file no longer matches the team-approved hash.",
                {"declared": declared_hash, "actual": strategy.get("sha256")},
            )
        )
    strategy_schema = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "strategy-contract.schema.json"
    approved_contract = None
    implemented_contract = None
    for label, inventory_key in (
        ("approved", "approved_strategy_contract"),
        ("implemented", "implemented_strategy_contract"),
    ):
        record = inventory.get(inventory_key)
        if not record or record.get("kind") != "file":
            continue
        try:
            contract = json.loads(Path(record["path"]).read_text(encoding="utf-8"))
            if not isinstance(contract, dict):
                raise ValueError("contract root must be an object")
            findings.extend(contract_findings(contract, strategy_schema, label))
            findings.extend(semantic_contract_findings(Path(record["path"]), root, label))
            if label == "approved":
                approved_contract = contract
            else:
                implemented_contract = contract
        except Exception as exc:
            findings.append(finding("Blocker", "STRATEGY_CONTRACT_READ", f"{label}: {exc}"))
    if approved_contract is not None and approved_contract.get("open_decisions"):
        findings.append(
            finding(
                "Blocker",
                "APPROVED_STRATEGY_NOT_SOLVER_READY",
                "The approved strategy contract still contains open governing decisions.",
                approved_contract.get("open_decisions"),
            )
        )

    core_fields = (
        "source_manifest",
        "source_reconciliation",
        "subproblems",
        "workbook_range_mappings",
        "information_structure",
        "model_route.recommended",
        "model_route.structural_insight",
        "formulation",
        "validation.acceptance_thresholds",
        "output_contract",
        "locked_decisions",
    )
    computed_differences = []
    if approved_contract is not None and implemented_contract is not None:
        for field in core_fields:
            try:
                if nested(approved_contract, field) != nested(implemented_contract, field):
                    computed_differences.append(field)
            except Exception as exc:
                findings.append(finding("Blocker", "STRATEGY_CONTRACT_FIELD", f"{field}: {exc}"))
    declared_difference_items = comparison.get("differences", []) if isinstance(comparison.get("differences"), list) else []
    declared_differences = {
        str(item.get("field", "")): item
        for item in declared_difference_items
        if isinstance(item, dict) and str(item.get("field", ""))
    }
    undeclared = sorted(set(computed_differences) - set(declared_differences))
    if undeclared:
        findings.append(
            finding(
                "Blocker",
                "UNDECLARED_STRATEGY_DIFFERENCE",
                "Implemented strategy contract differs from the approved contract without declaration.",
                undeclared,
            )
        )
    unresolved = {
        field: declared_differences.get(field, {}).get("disposition", "missing")
        for field in computed_differences
        if declared_differences.get(field, {}).get("disposition") not in {"team-approved", "non-material"}
    }
    if unresolved:
        findings.append(
            finding(
                "Critical",
                "UNRESOLVED_STRATEGY_DIFFERENCE",
                "Strategy differences require an explicit team disposition before audit release.",
                unresolved,
            )
        )
    scope = payload.get("declared_scope") if isinstance(payload.get("declared_scope"), dict) else {}
    if computed_differences and not scope.get("core_model_changed"):
        findings.append(
            finding(
                "Blocker",
                "FALSE_NO_CORE_CHANGE_DECLARATION",
                "The manifest declares no core change although structured contracts differ.",
                computed_differences,
            )
        )
    approved_members = {str(value).strip() for value in approved_strategy.get("approved_by", []) if str(value).strip()}
    comparison_reviewers = {str(value).strip() for value in comparison.get("reviewed_by", []) if str(value).strip()}
    if not comparison_reviewers or not comparison_reviewers <= approved_members:
        findings.append(
            finding(
                "Critical",
                "STRATEGY_COMPARISON_REVIEWER",
                "Strategy comparison must be reviewed by member(s) who approved the strategy.",
                {"reviewers": sorted(comparison_reviewers), "approved_by": sorted(approved_members)},
            )
        )
    try:
        stamp = datetime.fromisoformat(str(comparison.get("reviewed_at", "")).replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("timezone offset is required")
    except Exception as exc:
        findings.append(
            finding(
                "Critical",
                "STRATEGY_COMPARISON_TIMESTAMP",
                f"reviewed_at must be an ISO timestamp with timezone: {exc}",
                comparison.get("reviewed_at"),
            )
        )
    if scope.get("core_model_changed") or not scope.get("followed_approved_strategy", False):
        findings.append(
            finding(
                "Critical",
                "UNAPPROVED_CORE_CHANGE",
                "The external baseline changed or did not follow the approved core specification; open a new team decision gate before adoption.",
                scope.get("changes", []),
            )
        )
    screening = payload.get("team_screening") if isinstance(payload.get("team_screening"), dict) else {}
    if screening.get("decision") != "accepted_for_audit":
        findings.append(
            finding(
                "Critical",
                "QUARANTINE_NOT_RELEASED",
                "The team has not marked the bundle accepted_for_audit. This status never means accepted for submission.",
                screening,
            )
        )
    if screening.get("decision") == "accepted_for_audit":
        if not screening.get("screened_by") or not screening.get("screened_at"):
            findings.append(
                finding(
                    "Critical",
                    "SCREENING_EVIDENCE",
                    "accepted_for_audit requires the screening member(s) and timestamp.",
                    screening,
                )
            )
    return {
        "manifest": str(manifest_path),
        "root": str(root),
        "inventory": inventory,
        "findings": findings,
        "next_gate": "static paper/code QA, clean execution, independent verification, result-ledger reconciliation",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.manifest.is_file():
        print(json.dumps({"error": "handoff manifest not found"}, ensure_ascii=False))
        return 2
    root = (args.root or args.manifest.parent).resolve()
    schema = args.schema or (
        Path(__file__).resolve().parent.parent / "assets" / "schemas" / "external-baseline-handoff.schema.json"
    )
    report = inspect(args.manifest.resolve(), root, schema.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
