#!/usr/bin/env python3
"""Select historical CUMCM isolation candidates without claiming they are already blind."""

from __future__ import annotations

import argparse
import json
import random
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def check_url(url: str, timeout: int) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"mcm.edu.cn", "www.mcm.edu.cn"}:
        raise ValueError("benchmark source is not an official HTTPS mcm.edu.cn page")
    request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-skill-benchmark/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return {"status": response.status, "final_url": response.geturl()}


def select(catalog: Path, count: int, seed: int, online: bool, timeout: int) -> dict:
    payload = json.loads(catalog.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if payload.get("version") != 1 or not isinstance(cases, list) or not cases:
        raise ValueError("benchmark catalog must contain version 1 and nonempty cases")
    if count < 1 or count > len(cases):
        raise ValueError(f"count must be between 1 and {len(cases)}")
    rng = random.Random(seed)
    chosen = rng.sample(cases, count)
    findings = []
    output_cases = []
    for case in chosen:
        source_check = None
        if online:
            try:
                source_check = check_url(case["official_url"], timeout)
            except Exception as exc:
                findings.append(
                    finding("Critical", "BENCHMARK_SOURCE", f"{case.get('id')}: {exc}", case.get("official_url"))
                )
        output_cases.append(
            {
                "id": case["id"],
                "year": case["year"],
                "problem_letter": case["problem_letter"],
                "official_url": case["official_url"],
                "fresh_agent_task": case["fresh_agent_task"],
                "isolation_requirements": {
                    "create_resource_ledger_before_opening_problem": True,
                    "forbid_same_case_solution_material_before_freeze": True,
                    "audit_command": "python scripts/audit_benchmark_isolation.py LEDGER.json --root PROJECT --strict",
                    "capability_score_command": "python scripts/score_capability_benchmarks.py CAPABILITY_LEDGER.json --root PROJECT --strict",
                    "unblind_only_after_sha256_freeze": True,
                },
                "source_check": source_check,
                "evaluator_only": {
                    "artifact_lock_required": True,
                    "evaluation_focus": case["evaluation_focus"],
                    "scoring": {
                        "0": "missing or invalid",
                        "1": "present but generic",
                        "2": "specific and internally coherent",
                        "3": "strong, specific, falsifiable, executable, and traceable",
                        "4": "independently verified with consequential decision evidence"
                    },
                    "pass_rule": "Every canonical dimension >=2, at least four dimensions >=3, and no automatic failure."
                }
            }
        )
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "catalog": str(catalog),
        "seed": seed,
        "solution_blind": False,
        "solution_blind_status": "unverified_until_case_ledger_audit",
        "evidence_label": "historical_isolation_candidates",
        "cases": output_cases,
        "findings": findings
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "assets" / "benchmarks" / "cumcm-historical-cases.json",
    )
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        report = select(args.catalog.resolve(), args.count, args.seed, args.online, args.timeout)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
