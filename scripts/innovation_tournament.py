#!/usr/bin/env python3
"""Validate, rank, and freeze a problem-specific CUMCM structural-insight tournament."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = SKILL_ROOT / "assets" / "schemas" / "innovation-tournament.schema.json"
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
DEEP_FAMILIES = {
    "structural_reduction",
    "regime_switching",
    "identifiability",
    "uncertainty_decision",
    "strategy_boundary",
    "decision_focused_learning",
}
NON_HUMAN = re.compile(r"(?i)(?:\bai\b|\bgpt\b|\bcodex\b|chatgpt|claude|assistant|模型|机器人)")
GENERIC_INNOVATION = re.compile(
    r"改进(?:遗传|粒子群|蚁群|模拟退火|神经网络|算法)|"
    r"自适应(?:交叉|变异|学习率|权重)|"
    r"熵权.{0,12}TOPSIS|BP\s*神经网络|模型融合|组合模型",
    re.I,
)


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


def load_weights(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("weights", {})
    weights = {name: float(raw.get(name, 0.0)) for name in DIMENSIONS}
    total = sum(weights.values())
    if total <= 0 or any(value < 0 or not math.isfinite(value) for value in weights.values()):
        raise ValueError("selector weights must be finite, nonnegative, and have a positive sum")
    return {name: value / total for name, value in weights.items()}


def validate_schema(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Innovation manifest was not checked with JSON Schema.")]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    output = []
    errors = Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)
    for error in sorted(errors, key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "MANIFEST_SCHEMA", f"{location}: {error.message}"))
    return output


def candidate_score(candidate: dict, weights: dict[str, float], max_primary_budget: float) -> dict:
    assessment = candidate.get("ai_assessment", {})
    raw = sum(float(assessment.get(name, 0.0)) * weights[name] for name in DIMENSIONS) * 25.0
    budget = float(candidate.get("minimum_experiment", {}).get("budget_hours", 0.0) or 0.0)
    overrun_penalty = max(0.0, budget - max_primary_budget) / max(max_primary_budget, 1e-9) * 20.0
    experiment_status = candidate.get("minimum_experiment", {}).get("status")
    failure_penalty = 100.0 if experiment_status == "fail" else 0.0
    return {
        "raw_score": round(raw, 3),
        "budget_hours": budget,
        "risk_penalty": round(overrun_penalty + failure_penalty, 3),
        "rank_score": round(raw - overrun_penalty - failure_penalty, 3),
    }


def safe_project_file(root: Path, raw: str) -> Path:
    path = Path(raw)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    resolved.relative_to(root.resolve())
    return resolved


def substantive(value: Any, minimum: int = 12) -> bool:
    return isinstance(value, str) and len(re.sub(r"\s+", "", value)) >= minimum


def inspect(
    payload: dict,
    root: Path,
    phase: str,
    weights: dict[str, float],
    schema_path: Path | None = None,
) -> dict:
    findings: list[dict] = []
    if schema_path:
        findings.extend(validate_schema(payload, schema_path))
    candidates = payload.get("candidates")
    if payload.get("version") != 1 or not isinstance(candidates, list):
        return {
            "phase": phase,
            "summary": {"candidate_count": 0, "family_count": 0},
            "rankings": [],
            "recommended_shortlist": [],
            "findings": findings
            + [finding("Blocker", "MANIFEST_SHAPE", "Expected version 1 and a candidates array.")],
        }
    blind = payload.get("blind_context", {})
    if (
        blind.get("mode") in {"live_competition", "prospective_canary", "solution_isolated_historical"}
        and not blind.get("solution_blind")
    ):
        findings.append(
            finding(
                "Blocker",
                "BLIND_CONTEXT_CONTRADICTION",
                "The declared mode requires solution_blind=true; otherwise label it retrospective_rehearsal.",
            )
        )
    identifiers = [str(item.get("id", "")).strip() for item in candidates if isinstance(item, dict)]
    duplicates = sorted({identifier for identifier in identifiers if identifier and identifiers.count(identifier) > 1})
    if duplicates:
        findings.append(finding("Blocker", "DUPLICATE_CANDIDATE_ID", "Candidate IDs must be unique.", duplicates))
    if len(candidates) < 8:
        findings.append(
            finding(
                "Critical",
                "IDEA_POOL_TOO_SMALL",
                "National-first-oriented discovery requires at least eight structural hypotheses before selection.",
                len(candidates),
            )
        )
    families = {item.get("family") for item in candidates if isinstance(item, dict) and item.get("family")}
    if len(families) < 4:
        findings.append(
            finding(
                "Critical",
                "INSUFFICIENT_FAMILY_DIVERSITY",
                "The idea pool must span at least four materially different structural families.",
                sorted(families),
            )
        )
    max_primary_budget = float(payload.get("constraints", {}).get("max_primary_budget_hours", 0.0) or 0.0)
    if max_primary_budget <= 0:
        findings.append(finding("Blocker", "PRIMARY_BUDGET", "max_primary_budget_hours must be positive."))
        max_primary_budget = 1.0
    rankings = []
    candidate_map = {}
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            findings.append(finding("Blocker", "CANDIDATE_SHAPE", f"Candidate {index + 1} is not an object."))
            continue
        identifier = str(candidate.get("id", "")).strip()
        if identifier:
            candidate_map[identifier] = candidate
        required_text = (
            "insight_sentence",
            "baseline_failure",
            "structural_hypothesis",
            "exact_modification",
            "counterfactual",
            "expected_consequence",
            "falsifier",
            "fallback",
        )
        weak = [field for field in required_text if not substantive(candidate.get(field), 8)]
        if weak:
            findings.append(
                finding(
                    "Critical",
                    "THIN_INNOVATION_CLAIM",
                    f"Candidate {identifier or index + 1} lacks substantive fields.",
                    weak,
                )
            )
        if not candidate.get("problem_evidence"):
            findings.append(
                finding("Critical", "NO_PROBLEM_EVIDENCE", f"Candidate {identifier or index + 1} is not anchored to the prompt.")
            )
        changes = set(candidate.get("mathematical_object_changes") or [])
        if not changes:
            findings.append(
                finding(
                    "Critical",
                    "NO_MATHEMATICAL_CHANGE",
                    f"Candidate {identifier or index + 1} does not change a mathematical object.",
                )
            )
        blob = " ".join(str(candidate.get(field, "")) for field in ("title", "exact_modification", "insight_sentence"))
        if GENERIC_INNOVATION.search(blob) and changes <= {"solver"}:
            findings.append(
                finding(
                    "Critical",
                    "GENERIC_ALGORITHM_INNOVATION",
                    f"Candidate {identifier or index + 1} resembles generic algorithm tuning without a formulation change.",
                )
            )
        experiment = candidate.get("minimum_experiment", {})
        if not isinstance(experiment, dict):
            findings.append(finding("Critical", "NO_MICRO_EXPERIMENT", f"Candidate {identifier or index + 1} lacks a micro experiment."))
            experiment = {}
        if not substantive(experiment.get("independent_basis"), 12):
            findings.append(
                finding(
                    "Critical",
                    "WEAK_INDEPENDENCE",
                    f"Candidate {identifier or index + 1} does not explain what is independent about its pilot.",
                )
            )
        assessment = candidate.get("ai_assessment", {})
        if not isinstance(assessment, dict) or any(name not in assessment for name in DIMENSIONS):
            findings.append(
                finding("Critical", "MISSING_AI_ASSESSMENT", f"Candidate {identifier or index + 1} lacks all selector dimensions.")
            )
        elif not any(float(assessment.get(name, 0.0)) > 0 for name in DIMENSIONS):
            findings.append(
                finding("Critical", "UNSCORED_CANDIDATE", f"Candidate {identifier or index + 1} still has placeholder scores.")
            )
        review = candidate.get("team_review")
        if review:
            reviewers = [str(value).strip() for value in review.get("reviewed_by", [])]
            invalid = [value for value in reviewers if not value or NON_HUMAN.search(value)]
            if invalid:
                findings.append(
                    finding(
                        "Blocker",
                        "NON_HUMAN_INNOVATION_REVIEW",
                        f"Candidate {identifier or index + 1} has an invalid human-review identity.",
                        invalid,
                    )
                )
        score = candidate_score(candidate, weights, max_primary_budget)
        rankings.append(
            {
                "id": identifier,
                "title": candidate.get("title"),
                "family": candidate.get("family"),
                "stage": candidate.get("stage"),
                **score,
            }
        )
    rankings.sort(key=lambda item: (-item["rank_score"], item["id"]))
    viable = [item for item in rankings if candidate_map.get(item["id"], {}).get("stage") != "rejected"]
    recommended = [item["id"] for item in viable[:3]]
    selection = payload.get("selection", {})
    shortlisted = selection.get("shortlisted") if isinstance(selection, dict) else []
    primary = selection.get("primary_candidate") if isinstance(selection, dict) else None
    supporting = selection.get("supporting_candidates") if isinstance(selection, dict) else []
    declared_ids = set(shortlisted or []) | set(supporting or []) | ({primary} if primary else set())
    unknown = sorted(identifier for identifier in declared_ids if identifier not in candidate_map)
    if unknown:
        findings.append(finding("Blocker", "UNKNOWN_SELECTION", "Selection references unknown candidates.", unknown))
    if phase == "discovery" and shortlisted and list(shortlisted) != recommended:
        findings.append(
            finding(
                "Major",
                "SELECTOR_OVERRIDE",
                "The declared shortlist differs from the deterministic AI recommendation; record the human rationale.",
                {"declared": shortlisted, "recommended": recommended},
            )
        )
    if phase == "freeze":
        if len(shortlisted or []) != 3:
            findings.append(finding("Critical", "SHORTLIST_SIZE", "Freeze requires exactly three piloted shortlist candidates."))
        if not primary:
            findings.append(finding("Blocker", "NO_PRIMARY_INNOVATION", "Freeze requires one selected primary innovation."))
        selected_ids = ([primary] if primary else []) + list(supporting or [])
        if not set(selected_ids).issubset(set(shortlisted or [])):
            findings.append(
                finding(
                    "Blocker",
                    "FINAL_SELECTION_OUTSIDE_SHORTLIST",
                    "Primary and supporting innovations must come from the three piloted shortlist candidates.",
                    selected_ids,
                )
            )
        if len(set(selected_ids)) != len(selected_ids):
            findings.append(finding("Blocker", "DUPLICATE_FINAL_SELECTION", "Primary and supporting candidates must be distinct."))
        for identifier in shortlisted or []:
            candidate = candidate_map.get(identifier)
            if not candidate:
                continue
            experiment = candidate.get("minimum_experiment", {})
            if experiment.get("status") not in {"pass", "fail"} or candidate.get("stage") not in {"validated", "rejected"}:
                findings.append(
                    finding(
                        "Blocker",
                        "SHORTLIST_PILOT_INCOMPLETE",
                        f"Shortlisted candidate {identifier} must finish its pilot before strategy freeze.",
                    )
                )
            evidence_file = experiment.get("evidence_file")
            evidence_hash = str(experiment.get("evidence_sha256", "")).lower()
            if not evidence_file or not evidence_hash:
                findings.append(
                    finding(
                        "Blocker",
                        "SHORTLIST_EVIDENCE_MISSING",
                        f"Shortlisted candidate {identifier} lacks hash-bound pilot evidence.",
                    )
                )
            else:
                try:
                    path = safe_project_file(root, evidence_file)
                    if not path.is_file():
                        raise FileNotFoundError(path)
                    actual = sha256(path)
                    if actual != evidence_hash:
                        findings.append(
                            finding(
                                "Blocker",
                                "SHORTLIST_EVIDENCE_HASH",
                                f"Shortlisted candidate {identifier} pilot evidence changed after review.",
                                {"declared": evidence_hash, "actual": actual},
                            )
                        )
                except Exception as exc:
                    findings.append(finding("Blocker", "SHORTLIST_EVIDENCE_READ", f"{identifier}: {exc}"))
            if not candidate.get("team_review"):
                findings.append(
                    finding(
                        "Blocker",
                        "SHORTLIST_REVIEW_MISSING",
                        f"Shortlisted candidate {identifier} lacks a recorded human review.",
                    )
                )
        total_budget = 0.0
        for identifier in selected_ids:
            candidate = candidate_map.get(identifier)
            if not candidate:
                continue
            expected_decision = "selected_primary" if identifier == primary else "selected_supporting"
            review = candidate.get("team_review") or {}
            if review.get("decision") != expected_decision:
                findings.append(
                    finding(
                        "Blocker",
                        "TEAM_SELECTION_MISSING",
                        f"Candidate {identifier} lacks the required human decision {expected_decision}.",
                    )
                )
            experiment = candidate.get("minimum_experiment", {})
            if candidate.get("stage") != "validated" or experiment.get("status") != "pass":
                findings.append(
                    finding(
                        "Blocker",
                        "UNVALIDATED_SELECTION",
                        f"Selected candidate {identifier} must have a passing pilot and stage=validated.",
                    )
                )
            evidence_file = experiment.get("evidence_file")
            evidence_hash = str(experiment.get("evidence_sha256", "")).lower()
            if not evidence_file or not evidence_hash:
                findings.append(
                    finding("Blocker", "PILOT_EVIDENCE_MISSING", f"Selected candidate {identifier} lacks bound pilot evidence.")
                )
            else:
                try:
                    path = safe_project_file(root, evidence_file)
                    if not path.is_file():
                        raise FileNotFoundError(path)
                    actual = sha256(path)
                    if actual != evidence_hash:
                        findings.append(
                            finding(
                                "Blocker",
                                "PILOT_EVIDENCE_HASH",
                                f"Selected candidate {identifier} pilot evidence changed after review.",
                                {"declared": evidence_hash, "actual": actual},
                            )
                        )
                except Exception as exc:
                    findings.append(finding("Blocker", "PILOT_EVIDENCE_READ", f"{identifier}: {exc}"))
            assessment = candidate.get("ai_assessment", {})
            if any(float(assessment.get(name, 0)) < 3 for name in ("specificity", "evidenceability", "consequence")):
                findings.append(
                    finding(
                        "Critical",
                        "WEAK_SELECTED_INNOVATION",
                        f"Selected candidate {identifier} does not clear the minimum specificity/evidence/consequence scores.",
                    )
                )
            total_budget += float(experiment.get("budget_hours", 0.0) or 0.0)
        innovation_budget = float(payload.get("constraints", {}).get("innovation_budget_hours", 0.0) or 0.0)
        if total_budget > innovation_budget:
            findings.append(
                finding(
                    "Critical",
                    "INNOVATION_BUDGET_EXCEEDED",
                    "Selected pilots exceed the total innovation budget.",
                    {"selected_hours": total_budget, "budget_hours": innovation_budget},
                )
            )
        if primary and candidate_map.get(primary, {}).get("family") not in DEEP_FAMILIES:
            findings.append(
                finding(
                    "Major",
                    "SUPPORTING_PATTERN_AS_PRIMARY",
                    "The primary innovation is usually stronger when it changes structure or decision semantics rather than only implementation/certification.",
                    candidate_map.get(primary, {}).get("family"),
                )
            )
    severities = {item["severity"] for item in findings}
    return {
        "phase": phase,
        "problem_id": payload.get("problem_id"),
        "summary": {
            "candidate_count": len(candidates),
            "family_count": len(families),
            "shortlist_count": len(shortlisted or []),
            "primary_candidate": primary,
            "supporting_count": len(supporting or []),
            "passed": not bool({"Blocker", "Critical"} & severities),
        },
        "weights": weights,
        "rankings": rankings,
        "recommended_shortlist": recommended,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--phase", choices=("discovery", "freeze"), default="discovery")
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        root = (args.root or args.manifest.parent).resolve()
        report = inspect(payload, root, args.phase, load_weights(args.weights), args.schema)
    except Exception as exc:
        report = {
            "phase": args.phase,
            "summary": {"candidate_count": 0, "family_count": 0, "passed": False},
            "rankings": [],
            "recommended_shortlist": [],
            "findings": [finding("Blocker", "TOURNAMENT_READ", str(exc))],
        }
    if args.manifest.is_file():
        report["tournament_file"] = str(args.manifest.resolve())
        report["tournament_sha256"] = sha256(args.manifest)
    if args.weights.is_file():
        report["selector_weights_file"] = str(args.weights.resolve())
        report["selector_weights_sha256"] = sha256(args.weights)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
