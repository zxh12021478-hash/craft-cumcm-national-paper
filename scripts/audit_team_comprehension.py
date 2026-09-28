#!/usr/bin/env python3
"""Validate a manual, cross-audited team comprehension record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TOPICS = (
    "problem_interpretation",
    "assumptions_and_scope",
    "variables_objective_constraints",
    "solver_and_parameters",
    "headline_results",
    "validation_and_uncertainty",
    "limitations_and_failure_conditions",
    "ai_use_and_human_changes",
)


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def inspect(path: Path, team_size: int) -> dict:
    findings: list[dict] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"file": str(path), "findings": [finding("Blocker", "AUDIT_JSON", str(exc))]}
    if not isinstance(payload, dict):
        return {"file": str(path), "findings": [finding("Blocker", "AUDIT_SCHEMA", "Audit root must be an object.")]}
    members = payload.get("members", [])
    if not isinstance(members, list):
        return {"file": str(path), "findings": [finding("Blocker", "AUDIT_SCHEMA", "members must be an array.")]}
    try:
        declared_minimum = int(payload.get("minimum_score", 3))
    except (TypeError, ValueError):
        declared_minimum = -1
    if declared_minimum != 3:
        findings.append(
            finding(
                "Blocker",
                "MINIMUM_SCORE_OVERRIDE",
                "The final comprehension threshold is fixed at 3 and cannot be lowered by the audited artifact.",
                declared_minimum,
            )
        )
    minimum = 3
    if len(members) != team_size:
        findings.append(finding("Critical", "TEAM_SIZE", f"Expected {team_size} audited members.", len(members)))
    if any(not isinstance(member, dict) for member in members):
        findings.append(finding("Blocker", "MEMBER_SCHEMA", "Every member record must be an object."))
        members = [member for member in members if isinstance(member, dict)]
    names = [str(member.get("name", "")).strip() for member in members]
    if len(set(names)) != len(names) or any(not name for name in names):
        findings.append(finding("Critical", "MEMBER_NAMES", "Member names must be nonempty and unique.", names))
    topic_max = {topic: 0 for topic in TOPICS}
    for member in members:
        name = str(member.get("name", "?"))
        scores = member.get("scores", {})
        if not isinstance(scores, dict):
            findings.append(finding("Blocker", "SCORES_SCHEMA", f"{name}: scores must be an object."))
            scores = {}
        missing = [topic for topic in TOPICS if topic not in scores]
        if missing:
            findings.append(finding("Critical", "TOPIC_MISSING", f"{name}: topics are missing.", missing))
        failed = {}
        for topic in TOPICS:
            try:
                score = int(scores.get(topic, -1))
            except (TypeError, ValueError):
                score = -1
            topic_max[topic] = max(topic_max[topic], score)
            if score < minimum or score > 5:
                failed[topic] = score
        if failed:
            findings.append(finding("Critical", "MEMBER_UNDERSTANDING", f"{name}: comprehension gate failed.", failed))
        if not str(member.get("challenge_question", "")).strip():
            findings.append(finding("Major", "NO_CHALLENGE", f"{name}: no counterfactual challenge question recorded."))
        if not str(member.get("answer_evidence", "")).strip():
            findings.append(finding("Critical", "NO_ANSWER_EVIDENCE", f"{name}: no answer evidence recorded."))
        auditor = str(member.get("audited_by", "")).strip()
        if not auditor or auditor == name or auditor not in names:
            findings.append(finding("Critical", "CROSS_AUDIT", f"{name}: audit must be performed by another member.", auditor))
    weak_coverage = {topic: score for topic, score in topic_max.items() if score < 4}
    if weak_coverage:
        findings.append(finding("Major", "NO_TOPIC_OWNER", "No member demonstrated level-4 command of some topics.", weak_coverage))
    return {
        "file": str(path),
        "team_size": len(members),
        "minimum_score": minimum,
        "topic_maximums": topic_max,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit", type=Path)
    parser.add_argument("--team-size", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.audit.is_file() or args.team_size < 1:
        print(json.dumps({"error": "audit must exist and team size must be positive"}, ensure_ascii=False))
        return 2
    report = inspect(args.audit.resolve(), args.team_size)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
