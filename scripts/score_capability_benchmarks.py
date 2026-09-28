#!/usr/bin/env python3
"""Score frozen CUMCM skill forward tests without turning them into award predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = SKILL_ROOT / "assets" / "schemas" / "capability-benchmark-ledger.schema.json"
DIMENSIONS = (
    "requirement_coverage",
    "formulation_validity",
    "structural_insight",
    "reproducibility",
    "independent_validation",
    "cross_artifact_consistency",
    "decision_value",
)
TASK_FAMILIES = {
    "evaluation-ranking",
    "forecasting-optimization",
    "classification-warning",
    "optimization-scheduling",
    "mechanism-simulation",
    "network-spatial",
    "sequential-control",
}
EVIDENCE_LEVELS = {"E1", "E2", "E3", "E4"}
EVIDENCE_WEIGHT = {
    "prospective_canary": 1.0,
    "solution_isolated_historical": 0.7,
    "cross_case_assisted_historical": 0.55,
    "retrospective_rehearsal": 0.25,
    "synthetic_forward_test": 0.2,
}
FREEZE_REQUIRED = {
    "prospective_canary",
    "solution_isolated_historical",
    "cross_case_assisted_historical",
}
NON_HUMAN = re.compile(r"(?i)(?:\bai\b|\bgpt\b|\bcodex\b|assistant|模型|机器人)")


def finding(severity: str, code: str, message: str, evidence: Any = None) -> dict:
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


def project_file(root: Path, raw: str) -> Path:
    path = Path(raw)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    resolved.relative_to(root.resolve())
    return resolved


def validate_schema(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Capability ledger was not fully schema-validated.")]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    return [
        finding(
            "Blocker",
            "SCHEMA",
            error.message,
            "/".join(str(part) for part in error.absolute_path),
        )
        for error in errors
    ]


def score_assessment(case_id: str, label: str, assessment: Any, findings: list[dict]) -> dict | None:
    if not isinstance(assessment, dict) or not isinstance(assessment.get("dimensions"), dict):
        findings.append(finding("Blocker", "ASSESSMENT_SHAPE", f"{case_id} {label} assessment is missing dimensions."))
        return None
    normalized = {}
    for dimension in DIMENSIONS:
        record = assessment["dimensions"].get(dimension)
        if not isinstance(record, dict):
            findings.append(finding("Blocker", "DIMENSION_MISSING", f"{case_id} {label} misses {dimension}."))
            continue
        try:
            score = float(record.get("score"))
        except (TypeError, ValueError):
            score = math.nan
        evidence = record.get("evidence")
        if not math.isfinite(score) or not 0 <= score <= 4:
            findings.append(finding("Blocker", "DIMENSION_SCORE", f"{case_id} {label} has an invalid {dimension} score."))
            continue
        if not isinstance(evidence, list) or not evidence or any(len(str(item).strip()) < 3 for item in evidence):
            findings.append(finding("Blocker", "DIMENSION_EVIDENCE", f"{case_id} {label} lacks evidence for {dimension}."))
            continue
        normalized[dimension] = score
    if len(normalized) != len(DIMENSIONS):
        return None
    values = list(normalized.values())
    passed = min(values) >= 2 and sum(value >= 3 for value in values) >= 4
    return {
        "scores": normalized,
        "mean": statistics.fmean(values),
        "minimum": min(values),
        "strong_dimension_count": sum(value >= 3 for value in values),
        "passed": passed,
    }


def weighted_means(rows: list[tuple[dict[str, float], float]]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for dimension in DIMENSIONS:
        denominator = sum(weight for _, weight in rows)
        result[dimension] = (
            round(sum(scores[dimension] * weight for scores, weight in rows) / denominator, 4)
            if denominator
            else None
        )
    return result


def inspect(payload: dict, root: Path, schema_path: Path | None = None) -> dict:
    findings: list[dict] = []
    if schema_path:
        findings.extend(validate_schema(payload, schema_path))
    cases = payload.get("cases")
    if payload.get("version") != 1 or not isinstance(cases, list):
        return {
            "status": "blocked",
            "metrics": {},
            "cases": [],
            "findings": findings + [finding("Blocker", "LEDGER_SHAPE", "Expected version 1 and a cases array.")],
        }

    seen: set[str] = set()
    reports = []
    self_rows: list[tuple[dict[str, float], float]] = []
    independent_rows: list[tuple[dict[str, float], float]] = []
    independent_means = []
    self_means = []
    score_gaps = []
    elapsed = []
    interventions = []
    family_stats: dict[str, dict[str, int]] = {}
    effective_cases = 0.0
    prospective_count = 0
    independent_passes = 0
    regression = False

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            findings.append(finding("Blocker", "CASE_SHAPE", f"Case {index + 1} is not an object."))
            continue
        case_id = str(case.get("case_id", "")).strip()
        if not case_id or case_id in seen:
            findings.append(finding("Blocker", "CASE_ID", "Case IDs must be nonempty and unique.", case_id))
            continue
        seen.add(case_id)
        family = str(case.get("task_family", ""))
        label = str(case.get("isolation_label", ""))
        weight = EVIDENCE_WEIGHT.get(label, 0.0)
        case_blocked = False
        if family not in TASK_FAMILIES:
            findings.append(finding("Blocker", "TASK_FAMILY", f"{case_id} has an unknown task family.", family))
            case_blocked = True
        if label not in EVIDENCE_WEIGHT:
            findings.append(finding("Blocker", "ISOLATION_LABEL", f"{case_id} has an unknown isolation label.", label))
            case_blocked = True
        if case.get("evidence_level") not in EVIDENCE_LEVELS:
            findings.append(finding("Blocker", "EVIDENCE_LEVEL", f"{case_id} has an invalid evidence level.", case.get("evidence_level")))
            case_blocked = True
        if label in FREEZE_REQUIRED and not case.get("frozen_before_unblinding"):
            findings.append(finding("Blocker", "NOT_FROZEN", f"{case_id} was not frozen before unblinding."))
            case_blocked = True
        frozen = case.get("frozen_artifact", {})
        try:
            path = project_file(root, str(frozen.get("file", "")))
            if not path.is_file():
                raise FileNotFoundError(path)
            actual_hash = sha256(path)
            declared_hash = str(frozen.get("sha256", "")).lower()
            if actual_hash != declared_hash:
                findings.append(
                    finding("Blocker", "FROZEN_HASH_MISMATCH", f"{case_id} frozen artifact changed.", {"declared": declared_hash, "actual": actual_hash})
                )
                case_blocked = True
        except Exception as exc:
            findings.append(finding("Blocker", "FROZEN_ARTIFACT", f"{case_id}: {exc}"))
            case_blocked = True

        self_result = score_assessment(case_id, "self", case.get("self_assessment"), findings)
        independent = case.get("independent_assessment")
        independent_result = None
        reviewer_type = None
        if independent is not None:
            reviewer_type = independent.get("reviewer_type") if isinstance(independent, dict) else None
            reviewers = independent.get("reviewers", []) if isinstance(independent, dict) else []
            if reviewer_type not in {"independent_ai", "human"} or not reviewers:
                findings.append(finding("Blocker", "INDEPENDENT_REVIEWER", f"{case_id} has invalid independent reviewer metadata."))
                case_blocked = True
            elif reviewer_type == "human" and any(NON_HUMAN.search(str(name)) for name in reviewers):
                findings.append(finding("Blocker", "NON_HUMAN_REVIEW", f"{case_id} labels a non-human reviewer as human.", reviewers))
                case_blocked = True
            independent_result = score_assessment(case_id, "independent", independent, findings)

        automatic_failures = case.get("automatic_failures", [])
        if not isinstance(automatic_failures, list):
            findings.append(finding("Blocker", "AUTOMATIC_FAILURE_SHAPE", f"{case_id} automatic_failures must be an array."))
            automatic_failures = ["invalid automatic-failure record"]
            case_blocked = True
        if automatic_failures:
            findings.append(finding("Critical", "AUTOMATIC_FAILURE", f"{case_id} has non-negotiable failures.", automatic_failures))
            regression = True

        try:
            elapsed_value = float(case.get("elapsed_minutes", 0.0))
            intervention_value = int(case.get("human_interventions", 0))
            if elapsed_value < 0 or intervention_value < 0:
                raise ValueError("negative time or intervention count")
        except (TypeError, ValueError) as exc:
            findings.append(finding("Blocker", "EFFORT_METRIC", f"{case_id} has invalid effort metrics: {exc}"))
            elapsed_value = 0.0
            intervention_value = 0
            case_blocked = True
        elapsed.append(elapsed_value)
        interventions.append(intervention_value)
        if self_result:
            self_rows.append((self_result["scores"], weight))
            self_means.append(self_result["mean"])
        if independent_result:
            independent_rows.append((independent_result["scores"], weight))
            independent_means.append(independent_result["mean"])
            effective_cases += weight
            prospective_count += int(label == "prospective_canary")
            if self_result:
                gap = self_result["mean"] - independent_result["mean"]
                score_gaps.append(gap)
                if gap > 0.75:
                    findings.append(finding("Major", "SELF_OPTIMISM_GAP", f"{case_id} self-score exceeds independent score materially.", round(gap, 4)))
            case_passed = independent_result["passed"] and not automatic_failures and not case_blocked
            independent_passes += int(case_passed)
            if not case_passed:
                findings.append(finding("Critical", "CAPABILITY_CASE_FAILED", f"{case_id} did not pass the frozen independent rubric."))
                regression = True
        else:
            case_passed = False
            findings.append(finding("Major", "SELF_ONLY", f"{case_id} has no independent assessment."))

        family_entry = family_stats.setdefault(family or "unknown", {"cases": 0, "independent": 0, "passed": 0})
        family_entry["cases"] += 1
        family_entry["independent"] += int(independent_result is not None)
        family_entry["passed"] += int(case_passed)
        reports.append(
            {
                "case_id": case_id,
                "task_family": family,
                "isolation_label": label,
                "evidence_weight": weight,
                "self": self_result,
                "independent": independent_result,
                "reviewer_type": reviewer_type,
                "automatic_failures": automatic_failures,
                "status": "PASS" if case_passed else ("SELF_ONLY" if independent is None else "FAIL"),
            }
        )

    covered_families = sorted(
        family for family, counts in family_stats.items() if family in TASK_FAMILIES and counts["independent"] > 0
    )
    if any(item["severity"] == "Blocker" for item in findings):
        status = "blocked"
    elif regression:
        status = "regression_detected"
    elif effective_cases >= 6 and len(covered_families) >= 5 and prospective_count >= 1:
        status = "broad_capability_evidence"
    elif effective_cases >= 3 and len(covered_families) >= 3:
        status = "provisional_capability_evidence"
    else:
        status = "diagnostic_only"
        findings.append(
            finding(
                "Major",
                "INSUFFICIENT_CAPABILITY_EVIDENCE",
                "Keep claims diagnostic until independent evidence covers enough weighted cases and task families.",
                {"effective_cases": round(effective_cases, 3), "family_count": len(covered_families), "prospective_cases": prospective_count},
            )
        )

    independent_count = len(independent_rows)
    metrics = {
        "case_count": len(cases),
        "independently_assessed_cases": independent_count,
        "effective_case_count": round(effective_cases, 3),
        "task_family_count": len(covered_families),
        "task_families": covered_families,
        "prospective_case_count": prospective_count,
        "independent_pass_rate": round(independent_passes / independent_count, 4) if independent_count else None,
        "mean_self_score": round(statistics.fmean(self_means), 4) if self_means else None,
        "mean_independent_score": round(statistics.fmean(independent_means), 4) if independent_means else None,
        "mean_self_minus_independent": round(statistics.fmean(score_gaps), 4) if score_gaps else None,
        "median_elapsed_minutes": round(statistics.median(elapsed), 3) if elapsed else None,
        "median_human_interventions": statistics.median(interventions) if interventions else None,
        "self_dimension_means": weighted_means(self_rows),
        "independent_dimension_means": weighted_means(independent_rows),
    }
    return {
        "status": status,
        "award_prediction": None,
        "metrics": metrics,
        "task_family_summary": family_stats,
        "cases": reports,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
        root = (args.root or args.ledger.parent).resolve()
        report = inspect(payload, root, args.schema)
    except Exception as exc:
        report = {"status": "blocked", "metrics": {}, "cases": [], "findings": [finding("Blocker", "LEDGER_READ", str(exc))]}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
