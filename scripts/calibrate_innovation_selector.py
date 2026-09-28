#!/usr/bin/env python3
"""Audit blind-test outcomes and propose bounded innovation-selector weight updates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = SKILL_ROOT / "assets" / "schemas" / "innovation-calibration-ledger.schema.json"
DEFAULT_WEIGHTS = SKILL_ROOT / "assets" / "workflows" / "innovation-selector-weights.json"
DIMENSIONS = (
    "specificity",
    "necessity",
    "evidenceability",
    "consequence",
    "feasibility",
    "independence",
    "paper_value",
)
EVIDENCE_WEIGHT = {
    "prospective_canary": 1.0,
    "solution_isolated_historical": 0.7,
    "cross_case_assisted_historical": 0.55,
    "retrospective_rehearsal": 0.25,
}
TASK_FAMILIES = {
    "evaluation-ranking",
    "forecasting-optimization",
    "classification-warning",
    "optimization-scheduling",
    "mechanism-simulation",
    "network-spatial",
    "sequential-control",
}
NON_HUMAN = re.compile(r"(?i)(?:\bai\b|\bgpt\b|\bcodex\b|chatgpt|claude|assistant|模型|机器人)")


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


def validate_schema(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Calibration ledger was not checked with JSON Schema.")]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    output = []
    errors = Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)
    for error in sorted(errors, key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "LEDGER_SCHEMA", f"{location}: {error.message}"))
    return output


def load_base_weights(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = {name: float(payload.get("weights", {}).get(name, 0.0)) for name in DIMENSIONS}
    total = sum(values.values())
    if total <= 0 or any(value < 0 or not math.isfinite(value) for value in values.values()):
        raise ValueError("invalid base weights")
    return {name: value / total for name, value in values.items()}


def rank_candidates(tournament: dict, weights: dict[str, float]) -> list[str]:
    rows = []
    for candidate in tournament.get("candidates", []):
        if not isinstance(candidate, dict) or candidate.get("stage") == "rejected":
            continue
        assessment = candidate.get("ai_assessment", {})
        score = sum(float(assessment.get(name, 0.0)) * weights[name] for name in DIMENSIONS)
        rows.append((score, str(candidate.get("id", ""))))
    rows.sort(key=lambda item: (-item[0], item[1]))
    return [identifier for _, identifier in rows]


def weighted_correlation(points: list[tuple[float, float, float]]) -> float:
    total_weight = sum(weight for _, _, weight in points)
    if total_weight <= 0 or len(points) < 2:
        return 0.0
    mean_x = sum(x * weight for x, _, weight in points) / total_weight
    mean_y = sum(y * weight for _, y, weight in points) / total_weight
    covariance = sum(weight * (x - mean_x) * (y - mean_y) for x, y, weight in points)
    variance_x = sum(weight * (x - mean_x) ** 2 for x, _, weight in points)
    variance_y = sum(weight * (y - mean_y) ** 2 for _, y, weight in points)
    if variance_x <= 1e-12 or variance_y <= 1e-12:
        return 0.0
    return max(-1.0, min(1.0, covariance / math.sqrt(variance_x * variance_y)))


def normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    return {name: value / total for name, value in values.items()}


def inspect(
    payload: dict,
    root: Path,
    base_weights: dict[str, float],
    schema_path: Path | None = None,
) -> dict:
    findings: list[dict] = []
    if schema_path:
        findings.extend(validate_schema(payload, schema_path))
    cases = payload.get("cases")
    if payload.get("version") != 1 or not isinstance(cases, list):
        return {
            "status": "blocked",
            "metrics": {},
            "base_weights": base_weights,
            "recommended_weights": base_weights,
            "findings": findings + [finding("Blocker", "LEDGER_SHAPE", "Expected version 1 and a cases array.")],
        }
    case_reports = []
    feature_points: dict[str, list[tuple[float, float, float]]] = {name: [] for name in DIMENSIONS}
    top1_hits = 0
    top3_hits = 0
    evaluable_cases = 0
    effective_cases = 0.0
    false_novelty_top3 = 0
    evaluated_top3 = 0
    implemented = 0
    survived = 0
    regrets = []
    family_stats: dict[str, dict[str, int]] = {}
    for case in cases:
        if not isinstance(case, dict):
            findings.append(finding("Blocker", "CASE_SHAPE", "Every calibration case must be an object."))
            continue
        case_id = str(case.get("case_id", "")).strip()
        label = case.get("isolation_label")
        task_family = str(case.get("task_family", "")).strip()
        if task_family not in TASK_FAMILIES:
            findings.append(
                finding(
                    "Major",
                    "TASK_FAMILY_MISSING",
                    f"Case {case_id} cannot support cross-family calibration without a canonical task family.",
                    task_family,
                )
            )
        evidence_weight = EVIDENCE_WEIGHT.get(label, 0.0)
        if not case.get("frozen_before_unblinding"):
            findings.append(
                finding(
                    "Blocker",
                    "NOT_FROZEN_BEFORE_UNBLINDING",
                    f"Case {case_id} cannot calibrate the selector because the tournament was not frozen first.",
                )
            )
            continue
        reviewers = [str(value).strip() for value in case.get("human_review", {}).get("reviewers", [])]
        invalid_reviewers = [value for value in reviewers if not value or NON_HUMAN.search(value)]
        if invalid_reviewers:
            findings.append(
                finding(
                    "Blocker",
                    "NON_HUMAN_CALIBRATION_REVIEW",
                    f"Case {case_id} has an invalid human reviewer.",
                    invalid_reviewers,
                )
            )
            continue
        frozen = case.get("frozen_tournament", {})
        try:
            path = Path(str(frozen.get("file", "")))
            tournament_path = path.resolve() if path.is_absolute() else (root / path).resolve()
            tournament_path.relative_to(root.resolve())
            if not tournament_path.is_file():
                raise FileNotFoundError(tournament_path)
            actual_hash = sha256(tournament_path)
            declared_hash = str(frozen.get("sha256", "")).lower()
            if actual_hash != declared_hash:
                findings.append(
                    finding(
                        "Blocker",
                        "TOURNAMENT_HASH_MISMATCH",
                        f"Case {case_id} frozen tournament changed after review.",
                        {"declared": declared_hash, "actual": actual_hash},
                    )
                )
                continue
            tournament = json.loads(tournament_path.read_text(encoding="utf-8"))
        except Exception as exc:
            findings.append(finding("Blocker", "TOURNAMENT_READ", f"Case {case_id}: {exc}"))
            continue
        candidates = {
            str(item.get("id")): item
            for item in tournament.get("candidates", [])
            if isinstance(item, dict) and item.get("id")
        }
        predicted = rank_candidates(tournament, base_weights)
        outcomes = case.get("human_review", {}).get("candidate_outcomes", [])
        outcome_map = {
            str(item.get("candidate_id")): item
            for item in outcomes
            if isinstance(item, dict) and item.get("candidate_id")
        }
        unknown = sorted(set(outcome_map) - set(candidates))
        if unknown:
            findings.append(
                finding("Blocker", "UNKNOWN_OUTCOME_CANDIDATE", f"Case {case_id} outcomes reference unknown candidates.", unknown)
            )
            continue
        human_best = str(case.get("human_review", {}).get("human_best_candidate", ""))
        if human_best not in candidates or human_best not in outcome_map:
            findings.append(
                finding("Blocker", "HUMAN_BEST_UNMAPPED", f"Case {case_id} human-best candidate is not fully mapped.", human_best)
            )
            continue
        maximum_human_score = max(float(item.get("human_value_score", 0.0)) for item in outcome_map.values())
        if float(outcome_map[human_best].get("human_value_score", 0.0)) < maximum_human_score:
            findings.append(
                finding(
                    "Critical",
                    "HUMAN_BEST_SCORE_CONTRADICTION",
                    f"Case {case_id} human-best candidate does not have the highest human value score.",
                )
            )
        missing_top3 = [identifier for identifier in predicted[:3] if identifier not in outcome_map]
        if missing_top3:
            findings.append(
                finding(
                    "Critical",
                    "TOP3_OUTCOME_MISSING",
                    f"Case {case_id} does not record outcomes for every predicted top-three candidate.",
                    missing_top3,
                )
            )
        evaluable_cases += 1
        effective_cases += evidence_weight
        top1_hits += int(bool(predicted) and human_best == predicted[0])
        top3_hits += int(human_best in predicted[:3])
        family_entry = family_stats.setdefault(
            task_family or "unclassified",
            {"cases": 0, "top1_hits": 0, "top3_hits": 0, "evaluated_top3": 0, "false_novelty_top3": 0},
        )
        family_entry["cases"] += 1
        family_entry["top1_hits"] += int(bool(predicted) and human_best == predicted[0])
        family_entry["top3_hits"] += int(human_best in predicted[:3])
        for identifier in predicted[:3]:
            outcome = outcome_map.get(identifier)
            if outcome:
                evaluated_top3 += 1
                false_novelty_top3 += int(bool(outcome.get("false_novelty")))
                family_entry["evaluated_top3"] += 1
                family_entry["false_novelty_top3"] += int(bool(outcome.get("false_novelty")))
        for identifier, outcome in outcome_map.items():
            candidate = candidates[identifier]
            human_score = float(outcome.get("human_value_score", 0.0))
            for dimension in DIMENSIONS:
                feature_points[dimension].append(
                    (
                        float(candidate.get("ai_assessment", {}).get(dimension, 0.0)),
                        human_score,
                        evidence_weight,
                    )
                )
            if outcome.get("implemented"):
                implemented += 1
                survived += int(outcome.get("experiment_passed") is True and not outcome.get("false_novelty"))
        selected_scores = [
            float(item.get("human_value_score", 0.0))
            for item in outcome_map.values()
            if item.get("selected_final")
        ]
        if selected_scores:
            regrets.append(maximum_human_score - max(selected_scores))
        case_reports.append(
            {
                "case_id": case_id,
                "task_family": task_family,
                "isolation_label": label,
                "evidence_weight": evidence_weight,
                "predicted_top3": predicted[:3],
                "human_best_candidate": human_best,
                "top1_hit": bool(predicted) and human_best == predicted[0],
                "top3_hit": human_best in predicted[:3],
            }
        )
    labeled_points = max((len(values) for values in feature_points.values()), default=0)
    covered_families = sorted(family for family in family_stats if family in TASK_FAMILIES)
    if effective_cases >= 6 and labeled_points >= 24 and len(covered_families) >= 4:
        status = "calibrated_candidate_pending_team_approval"
        shrinkage = 0.5
    elif effective_cases >= 3 and labeled_points >= 12 and len(covered_families) >= 3:
        status = "provisional_pending_team_approval"
        shrinkage = 0.25
    else:
        status = "diagnostic_only"
        shrinkage = 0.0
        findings.append(
            finding(
                "Major",
                "INSUFFICIENT_CALIBRATION",
                "Keep default weights until evidence covers enough prospective-equivalent cases, labeled candidates, and task families.",
                {"effective_cases": round(effective_cases, 3), "labeled_candidates": labeled_points, "task_family_count": len(covered_families)},
            )
        )
    correlations = {
        dimension: weighted_correlation(feature_points[dimension])
        for dimension in DIMENSIONS
    }
    target = normalize(
        {
            dimension: base_weights[dimension] * (1.0 + 0.5 * correlations[dimension])
            for dimension in DIMENSIONS
        }
    )
    recommended = normalize(
        {
            dimension: (1.0 - shrinkage) * base_weights[dimension] + shrinkage * target[dimension]
            for dimension in DIMENSIONS
        }
    )
    metrics = {
        "case_count": len(cases),
        "evaluable_cases": evaluable_cases,
        "effective_case_count": round(effective_cases, 3),
        "labeled_candidates": labeled_points,
        "task_family_count": len(covered_families),
        "task_families": covered_families,
        "top1_hit_rate": round(top1_hits / evaluable_cases, 4) if evaluable_cases else None,
        "top3_hit_rate": round(top3_hits / evaluable_cases, 4) if evaluable_cases else None,
        "top3_false_novelty_rate": round(false_novelty_top3 / evaluated_top3, 4) if evaluated_top3 else None,
        "implemented_survival_rate": round(survived / implemented, 4) if implemented else None,
        "mean_selection_regret": round(sum(regrets) / len(regrets), 4) if regrets else None,
        "shrinkage": shrinkage,
    }
    per_family = {
        family: {
            **counts,
            "top1_hit_rate": round(counts["top1_hits"] / counts["cases"], 4) if counts["cases"] else None,
            "top3_hit_rate": round(counts["top3_hits"] / counts["cases"], 4) if counts["cases"] else None,
            "top3_false_novelty_rate": (
                round(counts["false_novelty_top3"] / counts["evaluated_top3"], 4)
                if counts["evaluated_top3"]
                else None
            ),
        }
        for family, counts in sorted(family_stats.items())
    }
    return {
        "status": status,
        "metrics": metrics,
        "case_reports": case_reports,
        "per_task_family": per_family,
        "dimension_correlations": {key: round(value, 4) for key, value in correlations.items()},
        "base_weights": {key: round(value, 6) for key, value in base_weights.items()},
        "recommended_weights": {key: round(value, 6) for key, value in recommended.items()},
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--base-weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-weights", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
        root = (args.root or args.ledger.parent).resolve()
        report = inspect(payload, root, load_base_weights(args.base_weights), args.schema)
    except Exception as exc:
        report = {
            "status": "blocked",
            "metrics": {},
            "base_weights": {},
            "recommended_weights": {},
            "findings": [finding("Blocker", "CALIBRATION_READ", str(exc))],
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.output_weights:
        package = {
            "version": 1,
            "status": report.get("status"),
            "dimensions": list(DIMENSIONS),
            "weights": report.get("recommended_weights", {}),
            "calibrated_from_cases": report.get("metrics", {}).get("evaluable_cases", 0),
            "effective_case_count": report.get("metrics", {}).get("effective_case_count", 0),
            "requires_team_approval_before_activation": True,
            "source_ledger_sha256": sha256(args.ledger) if args.ledger.is_file() else None,
        }
        args.output_weights.parent.mkdir(parents=True, exist_ok=True)
        args.output_weights.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
