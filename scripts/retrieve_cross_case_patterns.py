#!/usr/bin/env python3
"""Retrieve diverse cross-case structural cards from a target signature."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LIBRARY = (
    SKILL_ROOT / "assets" / "benchmarks" / "cross-case-structural-patterns.json"
)
DEFAULT_AWARD_EVIDENCE = (
    SKILL_ROOT / "assets" / "benchmarks" / "official-award-evidence.json"
)


def tokens(value: object) -> set[str]:
    if isinstance(value, list):
        output: set[str] = set()
        for item in value:
            output |= tokens(item)
        return output
    text = str(value or "").lower()
    return {
        token
        for token in re.split(r"[^0-9a-z_\-\u4e00-\u9fff]+", text)
        if token
    }


def score(
    card: dict,
    signature: dict,
    award_verified: bool = False,
) -> tuple[float, list[str]]:
    query = tokens(
        [
            signature.get("output"),
            signature.get("structures"),
            signature.get("constraints"),
            signature.get("bottlenecks"),
            signature.get("validation"),
            signature.get("keywords"),
        ]
    )
    tags = tokens(card.get("tags"))
    text = tokens(
        [
            card.get("move"),
            card.get("reconstruction_test"),
            card.get("counterfactual"),
            card.get("failure_risk"),
        ]
    )
    tag_hits = sorted(query & tags)
    text_hits = sorted(query & text)
    value = 4.0 * len(tag_hits) + 1.0 * len(text_hits)
    if card.get("kind") == "guardrail":
        guardrail_signals = {
            "classification",
            "high_accuracy",
            "small_sample",
            "correlation",
            "scenario",
            "stacking",
            "leakage",
        }
        if query & guardrail_signals:
            value += 5.0
    if card.get("provenance") == "third_party_bundle_unverified":
        value *= 0.55
    if award_verified and value > 0:
        value *= 1.08
    return value, tag_hits + text_hits


def year_of(source_case: str) -> int | None:
    match = re.search(r"(20\d{2})", source_case)
    return int(match.group(1)) if match else None


def normalized_case_id(value: object) -> str:
    """Normalize embedded CUMCM case labels such as CUMCM2023B-JMMIA to 2023B."""
    text = str(value or "").upper()
    match = re.search(r"(?:CUMCM)?[-_ ]?(20\d{2})[-_ ]?([A-E])(?:\b|[-_])", text)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return re.sub(r"[^0-9A-Z]", "", text)


def validate_award_links(library: dict, award_evidence: dict) -> list[str]:
    errors: list[str] = []
    records = award_evidence.get("records")
    if award_evidence.get("version") != 1 or not isinstance(records, list):
        return ["Award evidence must be a version-1 object with a records array."]

    record_ids = [record.get("id") for record in records]
    duplicate_records = sorted(
        {record_id for record_id in record_ids if record_ids.count(record_id) > 1}
    )
    if duplicate_records:
        errors.append(f"Duplicate award evidence IDs: {duplicate_records}")

    by_id = {
        record.get("id"): record
        for record in records
        if isinstance(record, dict) and record.get("id")
    }
    card_ids = [card.get("id") for card in library.get("cards", [])]
    duplicate_cards = sorted(
        {card_id for card_id in card_ids if card_ids.count(card_id) > 1}
    )
    if duplicate_cards:
        errors.append(f"Duplicate structural card IDs: {duplicate_cards}")

    for card in library.get("cards", []):
        verification = card.get("award_verification")
        if not verification:
            continue
        card_id = card.get("id", "<missing>")
        if verification.get("status") != "verified":
            errors.append(f"{card_id}: award_verification status must be verified.")
            continue
        evidence_id = verification.get("evidence_id")
        record = by_id.get(evidence_id)
        if not record:
            errors.append(f"{card_id}: missing award evidence record {evidence_id!r}.")
            continue
        if record.get("status") != "verified":
            errors.append(f"{card_id}: evidence {evidence_id} is not verified.")
        identity = record.get("identity_match") or {}
        if len(identity.get("keys") or []) < 2:
            errors.append(
                f"{card_id}: evidence {evidence_id} needs at least two identity keys."
            )
        roles = {
            source.get("role")
            for source in record.get("sources", [])
            if isinstance(source, dict)
        }
        if "official_award_source" not in roles:
            errors.append(
                f"{card_id}: evidence {evidence_id} lacks official_award_source."
            )
        if "paper_identity_source" not in roles:
            errors.append(
                f"{card_id}: evidence {evidence_id} lacks paper_identity_source."
            )
    return errors


def verified_award_records(award_evidence: dict | None) -> dict[str, dict]:
    if not award_evidence:
        return {}
    return {
        record["id"]: record
        for record in award_evidence.get("records", [])
        if isinstance(record, dict)
        and record.get("id")
        and record.get("status") == "verified"
    }


def inspect(
    signature: dict,
    library: dict,
    top_k: int,
    award_evidence: dict | None = None,
) -> dict:
    forbidden_raw = set(signature.get("forbidden_source_cases") or [])
    forbidden = {normalized_case_id(item) for item in forbidden_raw}
    evidence_errors = (
        validate_award_links(library, award_evidence)
        if award_evidence is not None
        else []
    )
    award_records = verified_award_records(award_evidence)
    ranked = []
    for card in library.get("cards", []):
        if normalized_case_id(card.get("source_case")) in forbidden:
            continue
        verification = card.get("award_verification") or {}
        evidence = award_records.get(verification.get("evidence_id"))
        award_verified = bool(
            verification.get("status") == "verified" and evidence
        )
        value, hits = score(card, signature, award_verified)
        ranked.append(
            {
                "id": card["id"],
                "source_case": card["source_case"],
                "year": year_of(card["source_case"]),
                "provenance": card["provenance"],
                "kind": card["kind"],
                "score": round(value, 3),
                "matched_terms": hits,
                "award_verified": award_verified,
                "award_evidence_id": (
                    verification.get("evidence_id") if award_verified else None
                ),
                "award_grade": (
                    evidence.get("award", {}).get("grade") if evidence else None
                ),
                "award_label": (
                    evidence.get("award", {}).get("label") if evidence else None
                ),
                "move": card["move"],
                "reconstruction_test": card["reconstruction_test"],
                "counterfactual": card["counterfactual"],
                "failure_risk": card["failure_risk"],
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["id"]))

    selected = []
    source_cases = set()
    for item in ranked:
        if len(selected) >= top_k:
            break
        if item["score"] <= 0 and selected:
            continue
        if item["source_case"] in source_cases and len(source_cases) < 2:
            continue
        selected.append(item)
        source_cases.add(item["source_case"])

    query = tokens(signature)
    needs_guardrail = bool(
        query
        & {
            "classification",
            "high_accuracy",
            "small_sample",
            "correlation",
            "scenario",
            "stacking",
            "leakage",
        }
    )
    if needs_guardrail and not any(item["kind"] == "guardrail" for item in selected):
        guardrail = next(
            (item for item in ranked if item["kind"] == "guardrail"),
            None,
        )
        if guardrail:
            selected = selected[: max(0, top_k - 1)] + [guardrail]

    return {
        "library_version": library.get("version"),
        "signature": signature,
        "selected": selected,
        "diagnostics": {
            "selected_count": len(selected),
            "distinct_source_cases": len({item["source_case"] for item in selected}),
            "distinct_years": len({item["year"] for item in selected if item["year"]}),
            "guardrail_required": needs_guardrail,
            "guardrail_present": any(item["kind"] == "guardrail" for item in selected),
            "award_verified_selected": sum(
                bool(item["award_verified"]) for item in selected
            ),
            "award_evidence_errors": evidence_errors,
            "award_boundary": library.get("policy", {}).get("award_boundary"),
            "award_weight_boundary": library.get("policy", {}).get(
                "award_weight_boundary"
            ),
            "same_case_boundary": library.get("policy", {}).get("same_case_boundary"),
            "normalized_forbidden_source_cases": sorted(forbidden),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("signature", type=Path)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument(
        "--award-evidence",
        type=Path,
        default=DEFAULT_AWARD_EVIDENCE,
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 3 <= args.top_k <= 7:
        raise SystemExit("--top-k must be between 3 and 7")
    signature = json.loads(args.signature.read_text(encoding="utf-8"))
    library = json.loads(args.library.read_text(encoding="utf-8"))
    award_evidence = json.loads(
        args.award_evidence.read_text(encoding="utf-8")
    )
    evidence_errors = validate_award_links(library, award_evidence)
    if evidence_errors:
        raise SystemExit(
            "Invalid award evidence links:\n- " + "\n- ".join(evidence_errors)
        )
    report = inspect(signature, library, args.top_k, award_evidence)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
