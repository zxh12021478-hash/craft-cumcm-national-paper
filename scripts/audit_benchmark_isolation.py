#!/usr/bin/env python3
"""Audit a CUMCM benchmark ledger for pre-freeze solution contamination."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


FORBIDDEN_CATEGORIES = {
    "same_case_solution",
    "official_sample_index",
    "official_sample_casebook",
    "award_paper",
    "public_code",
    "search_snippet",
}
FORBIDDEN_LOCATOR_MARKERS = {
    "official-sample-index",
    "official-sample-casebook",
    "sample-papers",
}


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def inspect(payload: dict, root: Path, schema: Path | None = None) -> dict:
    findings: list[dict] = []
    if schema:
        try:
            import jsonschema

            jsonschema.validate(payload, json.loads(schema.read_text(encoding="utf-8")))
        except ModuleNotFoundError:
            findings.append(
                finding("Major", "JSONSCHEMA_UNAVAILABLE", "Ledger was not checked with JSON Schema.")
            )
        except Exception as exc:
            findings.append(finding("Blocker", "LEDGER_SCHEMA", str(exc)))

    if payload.get("version") != 1:
        findings.append(finding("Blocker", "LEDGER_VERSION", "Ledger version must be 1."))

    stage = str(payload.get("stage", "")).strip()
    if not stage:
        # Backward compatibility for version-1 ledgers created before explicit lifecycle states.
        stage = "frozen" if payload.get("frozen_at") or payload.get("frozen_artifacts") else "pre_freeze"
    if stage not in {"pre_freeze", "frozen", "unblinded"}:
        findings.append(finding("Blocker", "LEDGER_STAGE", "Unknown benchmark lifecycle stage."))

    case_id = str(payload.get("case_id", "")).strip()
    for resource in payload.get("pre_freeze_resources", []):
        if not isinstance(resource, dict):
            findings.append(finding("Blocker", "RESOURCE_RECORD", "Resource record must be an object."))
            continue
        locator = str(resource.get("locator", ""))
        category = str(resource.get("category", "unknown"))
        scopes = {str(item).casefold() for item in resource.get("case_scope", [])}
        same_case = not scopes or case_id.casefold() in scopes or "all" in scopes
        marker_hit = any(marker in locator.casefold() for marker in FORBIDDEN_LOCATOR_MARKERS)
        if same_case and (marker_hit or category in FORBIDDEN_CATEGORIES):
            findings.append(
                finding(
                    "Blocker",
                    "BENCHMARK_CONTAMINATED",
                    "Same-case solution material was exposed before strategy freeze.",
                    {"locator": locator, "category": category, "case_scope": sorted(scopes)},
                )
            )
        elif category == "unknown":
            findings.append(
                finding("Major", "RESOURCE_UNKNOWN", "Classify the pre-freeze resource.", locator)
            )

    frozen_at = None
    unblinded_at = None
    try:
        frozen_at = parse_timestamp(payload.get("frozen_at"))
        unblinded_at = parse_timestamp(payload.get("unblinded_at"))
    except (TypeError, ValueError) as exc:
        findings.append(finding("Blocker", "TIMESTAMP_INVALID", str(exc)))
    if frozen_at and unblinded_at and unblinded_at < frozen_at:
        findings.append(
            finding("Blocker", "UNBLINDED_BEFORE_FREEZE", "Unblinding timestamp precedes freeze.")
        )

    artifacts = payload.get("frozen_artifacts", [])
    if stage == "pre_freeze":
        if artifacts or frozen_at or unblinded_at:
            findings.append(
                finding(
                    "Blocker",
                    "PRE_FREEZE_STATE_CONTRADICTION",
                    "A pre-freeze ledger cannot contain frozen artifacts or freeze/unblinding timestamps.",
                )
            )
        findings.append(
            finding(
                "Major",
                "FREEZE_PENDING",
                "Isolation ledger is initialized, but no strategy has been frozen yet.",
            )
        )
    elif not artifacts or frozen_at is None:
        findings.append(
            finding(
                "Blocker",
                "FREEZE_RECORD_INCOMPLETE",
                "Frozen or unblinded stages require at least one artifact and a valid freeze timestamp.",
            )
        )
    if stage == "frozen" and unblinded_at is not None:
        findings.append(
            finding("Blocker", "FROZEN_STAGE_HAS_UNBLINDING", "Frozen stage must not have an unblinding timestamp.")
        )
    if stage == "unblinded" and unblinded_at is None:
        findings.append(
            finding("Blocker", "UNBLINDED_TIME_MISSING", "Unblinded stage requires unblinded_at.")
        )

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            findings.append(finding("Blocker", "ARTIFACT_RECORD", "Artifact record must be an object."))
            continue
        candidate = Path(str(artifact.get("path", "")))
        path = candidate if candidate.is_absolute() else root / candidate
        if not path.is_file():
            findings.append(finding("Blocker", "FROZEN_ARTIFACT_MISSING", "Frozen artifact is missing.", str(path)))
            continue
        actual = file_sha256(path)
        expected = str(artifact.get("sha256", ""))
        if actual != expected:
            findings.append(
                finding(
                    "Blocker",
                    "FROZEN_HASH_MISMATCH",
                    "Frozen artifact hash does not match the ledger.",
                    {"path": str(path), "expected": expected, "actual": actual},
                )
            )

    if payload.get("prior_model_memory") == "known_same_case":
        findings.append(
            finding("Blocker", "KNOWN_SAME_CASE_MEMORY", "Known same-case solution memory invalidates isolation.")
        )
    elif payload.get("prior_model_memory") == "unknown":
        findings.append(
            finding(
                "Minor",
                "MODEL_MEMORY_UNKNOWN",
                "Historical isolation cannot establish zero-knowledge model memory; this limits the claim but does not invalidate solution isolation.",
            )
        )

    contaminated = any(item["code"] in {
        "BENCHMARK_CONTAMINATED",
        "KNOWN_SAME_CASE_MEMORY",
        "UNBLINDED_BEFORE_FREEZE",
    } for item in findings)
    invalid_freeze = any(item["code"] in {
        "FROZEN_ARTIFACT_MISSING",
        "FROZEN_HASH_MISMATCH",
        "TIMESTAMP_INVALID",
        "LEDGER_SCHEMA",
        "LEDGER_VERSION",
        "LEDGER_STAGE",
        "PRE_FREEZE_STATE_CONTRADICTION",
        "FREEZE_RECORD_INCOMPLETE",
        "FROZEN_STAGE_HAS_UNBLINDING",
        "UNBLINDED_TIME_MISSING",
    } for item in findings)

    if contaminated:
        evidence_label = "retrospective_rehearsal"
    elif stage == "pre_freeze" and not invalid_freeze:
        evidence_label = "pre_freeze_initialized"
    elif invalid_freeze:
        evidence_label = "invalid_benchmark_record"
    elif payload.get("evaluation_mode") == "prospective_unseen":
        evidence_label = "prospective_forward_test"
    elif payload.get("evaluation_mode") == "cross_case_assisted_historical":
        evidence_label = "cross_case_assisted_solution_isolated_historical_candidate"
    else:
        evidence_label = "solution_isolated_historical_candidate"

    declared_blind = bool(payload.get("declared_solution_blind"))
    if declared_blind and payload.get("evaluation_mode") in {
        "retrospective_historical",
        "cross_case_assisted_historical",
    }:
        findings.append(
            finding(
                "Major",
                "ZERO_KNOWLEDGE_OVERCLAIM",
                "A historical test may be solution-isolated, but should not be labeled zero-knowledge blind.",
            )
        )
    if declared_blind and (contaminated or invalid_freeze):
        findings.append(
            finding(
                "Blocker",
                "SOLUTION_BLIND_CONTRADICTION",
                "The ledger declares solution_blind despite contamination or an invalid freeze.",
            )
        )

    return {
        "benchmark_id": payload.get("benchmark_id"),
        "case_id": case_id,
        "stage": stage,
        "evidence_label": evidence_label,
        "solution_blind": bool(
            payload.get("evaluation_mode") == "prospective_unseen"
            and not contaminated
            and not invalid_freeze
        ),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not args.ledger.is_file():
        print(json.dumps({"error": "ledger not found"}, ensure_ascii=False))
        return 2
    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    root = (args.root or args.ledger.parent).resolve()
    schema = args.schema or (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "schemas"
        / "benchmark-isolation-ledger.schema.json"
    )
    report = inspect(payload, root, schema.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
