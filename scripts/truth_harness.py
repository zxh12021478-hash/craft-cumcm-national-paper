#!/usr/bin/env python3
"""Run small independent, deterministic truth checks across common CUMCM task families."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any


def finding(severity: str, code: str, message: str, evidence: Any = None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def nested_value(payload: Any, key: str) -> Any:
    current = payload
    for part in key.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(key)
    return current


def resolve(value: Any, root: Path) -> Any:
    if not isinstance(value, dict) or "source" not in value:
        return value
    source = value["source"]
    path = Path(source["file"])
    path = path if path.is_absolute() else root / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    return nested_value(payload, source["key"])


def point_distance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("point dimensions differ")
    return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(left, right)))


def check_constraint_set(check: dict, root: Path) -> tuple[bool, dict]:
    tolerance = float(resolve(check.get("tolerance", 1e-8), root))
    violations = {}
    for constraint in check.get("constraints", []):
        lhs = float(resolve(constraint["lhs"], root))
        rhs = float(resolve(constraint["rhs"], root))
        sense = constraint["sense"]
        if sense == "<=":
            violation = max(0.0, lhs - rhs)
        elif sense == ">=":
            violation = max(0.0, rhs - lhs)
        elif sense == "==":
            violation = abs(lhs - rhs)
        else:
            raise ValueError(f"unsupported constraint sense: {sense}")
        violations[constraint["name"]] = violation
    maximum = max(violations.values(), default=0.0)
    return maximum <= tolerance, {"max_violation": maximum, "tolerance": tolerance, "violations": violations}


def check_multi_seed(check: dict, root: Path) -> tuple[bool, dict]:
    values = [float(item) for item in resolve(check["values"], root)]
    minimum_count = int(check.get("min_count", 3))
    maximum_cv = float(check.get("max_cv", 0.05))
    mean = statistics.fmean(values) if values else math.nan
    if len(values) < 2 or abs(mean) <= 1e-15:
        cv = math.inf
    else:
        cv = statistics.pstdev(values) / abs(mean)
    passed = len(values) >= minimum_count and cv <= maximum_cv
    return passed, {"count": len(values), "mean": mean, "cv": cv, "max_cv": maximum_cv}


def check_conservation(check: dict, root: Path) -> tuple[bool, dict]:
    initial = float(resolve(check["initial"], root))
    incoming = float(resolve(check.get("input", 0.0), root))
    outgoing = float(resolve(check.get("output", 0.0), root))
    dissipation = float(resolve(check.get("dissipation", 0.0), root))
    final = float(resolve(check["final"], root))
    tolerance = float(check.get("tolerance", 1e-6))
    residual = initial + incoming - outgoing - dissipation - final
    return abs(residual) <= tolerance, {"residual": residual, "tolerance": tolerance}


def check_convergence(check: dict, root: Path) -> tuple[bool, dict]:
    coarse = float(resolve(check["coarse"], root))
    medium = float(resolve(check["medium"], root))
    fine = float(resolve(check["fine"], root))
    max_ratio = float(check.get("max_ratio", 0.75))
    first = abs(coarse - medium)
    second = abs(medium - fine)
    ratio = 0.0 if first == 0.0 and second == 0.0 else (math.inf if first == 0.0 else second / first)
    return ratio <= max_ratio, {"coarse_medium": first, "medium_fine": second, "ratio": ratio, "max_ratio": max_ratio}


def check_distance_invariance(check: dict, root: Path) -> tuple[bool, dict]:
    original = resolve(check["original_points"], root)
    transformed = resolve(check["transformed_points"], root)
    if len(original) != len(transformed):
        raise ValueError("point sets have different lengths")
    tolerance = float(check.get("tolerance", 1e-9))
    errors = []
    for first in range(len(original)):
        for second in range(first + 1, len(original)):
            errors.append(
                abs(
                    point_distance(original[first], original[second])
                    - point_distance(transformed[first], transformed[second])
                )
            )
    maximum = max(errors, default=0.0)
    return maximum <= tolerance, {"max_pairwise_distance_error": maximum, "tolerance": tolerance}


def check_roundtrip(check: dict, root: Path) -> tuple[bool, dict]:
    original = resolve(check["original_points"], root)
    recovered = resolve(check["recovered_points"], root)
    if len(original) != len(recovered):
        raise ValueError("point sets have different lengths")
    tolerance = float(check.get("tolerance", 1e-9))
    errors = [point_distance(left, right) for left, right in zip(original, recovered)]
    maximum = max(errors, default=0.0)
    return maximum <= tolerance, {"max_roundtrip_error": maximum, "tolerance": tolerance}


def check_split(check: dict, root: Path) -> tuple[bool, dict]:
    train = {str(item) for item in resolve(check["train_ids"], root)}
    test = {str(item) for item in resolve(check["test_ids"], root)}
    overlap = sorted(train & test)
    temporal_ok = True
    max_train = None
    min_test = None
    if check.get("require_temporal_order"):
        train_times = list(resolve(check["train_times"], root))
        test_times = list(resolve(check["test_times"], root))
        max_train = max(train_times)
        min_test = min(test_times)
        temporal_ok = max_train < min_test
    return not overlap and temporal_ok, {
        "overlap": overlap,
        "temporal_order_ok": temporal_ok,
        "max_train_time": max_train,
        "min_test_time": min_test,
    }


def check_metric(check: dict, root: Path) -> tuple[bool, dict]:
    proposed = float(resolve(check["proposed"], root))
    baseline = float(resolve(check["baseline"], root))
    direction = check.get("direction", "maximize")
    signed = proposed - baseline if direction == "maximize" else baseline - proposed
    relative = signed / abs(baseline) if abs(baseline) > 1e-15 else (math.inf if signed > 0 else 0.0)
    min_absolute = float(check.get("min_absolute_improvement", 0.0))
    min_relative = float(check.get("min_relative_improvement", 0.0))
    passed = signed >= min_absolute and relative >= min_relative
    return passed, {
        "proposed": proposed,
        "baseline": baseline,
        "absolute_improvement": signed,
        "relative_improvement": relative,
    }


def check_coverage(check: dict, root: Path) -> tuple[bool, dict]:
    if "hits" in check:
        hits = [bool(item) for item in resolve(check["hits"], root)]
        covered, total = sum(hits), len(hits)
    else:
        covered = int(resolve(check["covered"], root))
        total = int(resolve(check["total"], root))
    rate = covered / total if total else math.nan
    minimum = float(check.get("min_coverage", 0.0))
    maximum = float(check.get("max_coverage", 1.0))
    return total > 0 and minimum <= rate <= maximum, {
        "covered": covered,
        "total": total,
        "coverage": rate,
        "accepted_interval": [minimum, maximum],
    }


def check_range(check: dict, root: Path) -> tuple[bool, dict]:
    values = [float(item) for item in resolve(check["values"], root)]
    lower = float(check.get("minimum", -math.inf))
    upper = float(check.get("maximum", math.inf))
    outside = [value for value in values if value < lower or value > upper or not math.isfinite(value)]
    return not outside, {"count": len(values), "outside": outside, "accepted_interval": [lower, upper]}


def numeric_vector(value: Any) -> list[float]:
    if isinstance(value, list):
        return [float(item) for item in value]
    return [float(value)]


def check_independent_recompute(check: dict, root: Path) -> tuple[bool, dict]:
    primary = numeric_vector(resolve(check["primary"], root))
    independent = numeric_vector(resolve(check["independent"], root))
    if len(primary) != len(independent):
        raise ValueError("primary and independent values have different lengths")
    absolute_tolerance = float(check.get("absolute_tolerance", 1e-9))
    relative_tolerance = float(check.get("relative_tolerance", 1e-7))
    absolute_errors = [abs(left - right) for left, right in zip(primary, independent)]
    accepted = [
        absolute_tolerance + relative_tolerance * max(abs(left), abs(right))
        for left, right in zip(primary, independent)
    ]
    passed = all(error <= limit for error, limit in zip(absolute_errors, accepted))
    relative_errors = [
        error / max(abs(left), abs(right), 1e-15)
        for error, left, right in zip(absolute_errors, primary, independent)
    ]
    return passed, {
        "count": len(primary),
        "max_absolute_error": max(absolute_errors, default=0.0),
        "max_relative_error": max(relative_errors, default=0.0),
        "absolute_tolerance": absolute_tolerance,
        "relative_tolerance": relative_tolerance,
    }


def check_linear_objective(check: dict, root: Path) -> tuple[bool, dict]:
    coefficients = numeric_vector(resolve(check["coefficients"], root))
    variables = numeric_vector(resolve(check["variables"], root))
    if len(coefficients) != len(variables):
        raise ValueError("objective coefficients and variables have different lengths")
    constant = float(resolve(check.get("constant", 0.0), root))
    reported = float(resolve(check["reported_objective"], root))
    recomputed = constant + sum(coefficient * value for coefficient, value in zip(coefficients, variables))
    absolute_tolerance = float(check.get("absolute_tolerance", 1e-9))
    relative_tolerance = float(check.get("relative_tolerance", 1e-7))
    error = abs(recomputed - reported)
    limit = absolute_tolerance + relative_tolerance * max(abs(recomputed), abs(reported))
    return error <= limit, {
        "reported_objective": reported,
        "recomputed_objective": recomputed,
        "absolute_error": error,
        "accepted_error": limit,
    }


def check_matrix_constraints(check: dict, root: Path) -> tuple[bool, dict]:
    matrix = resolve(check["matrix"], root)
    variables = numeric_vector(resolve(check["variables"], root))
    if not isinstance(matrix, list) or any(not isinstance(row, list) for row in matrix):
        raise ValueError("constraint matrix must be a list of rows")
    if any(len(row) != len(variables) for row in matrix):
        raise ValueError("constraint row width does not match variable count")
    row_count = len(matrix)
    lower_raw = resolve(check.get("lower_bounds", [None] * row_count), root)
    upper_raw = resolve(check.get("upper_bounds", [None] * row_count), root)
    if len(lower_raw) != row_count or len(upper_raw) != row_count:
        raise ValueError("constraint bounds do not match matrix row count")
    tolerance = float(check.get("tolerance", 1e-8))
    activities = [sum(float(coefficient) * value for coefficient, value in zip(row, variables)) for row in matrix]
    violations = []
    for activity, lower, upper in zip(activities, lower_raw, upper_raw):
        lower_violation = 0.0 if lower is None else max(0.0, float(lower) - activity)
        upper_violation = 0.0 if upper is None else max(0.0, activity - float(upper))
        violations.append(max(lower_violation, upper_violation))
    maximum = max(violations, default=0.0)
    return maximum <= tolerance, {
        "activities": activities,
        "violations": violations,
        "max_violation": maximum,
        "tolerance": tolerance,
    }


CHECKERS = {
    "constraint_set": check_constraint_set,
    "multi_seed_stability": check_multi_seed,
    "conservation_balance": check_conservation,
    "step_convergence": check_convergence,
    "distance_invariance": check_distance_invariance,
    "roundtrip_error": check_roundtrip,
    "split_integrity": check_split,
    "metric_improvement": check_metric,
    "interval_coverage": check_coverage,
    "range": check_range,
    "independent_recompute": check_independent_recompute,
    "linear_objective_recompute": check_linear_objective,
    "matrix_constraint_recompute": check_matrix_constraints,
}


def inspect(payload: dict, root: Path) -> dict:
    findings = []
    results = []
    if payload.get("version") != 1 or not isinstance(payload.get("checks"), list):
        return {
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "checks": [],
            "findings": [finding("Blocker", "MANIFEST_SHAPE", "Manifest requires version 1 and a checks array.")],
        }
    seen = set()
    for check in payload["checks"]:
        identifier = str(check.get("id", ""))
        check_type = str(check.get("type", ""))
        if not identifier or identifier in seen:
            findings.append(finding("Blocker", "CHECK_ID", "Check IDs must be nonempty and unique.", identifier))
            continue
        seen.add(identifier)
        checker = CHECKERS.get(check_type)
        if checker is None:
            findings.append(finding("Blocker", "CHECK_TYPE", "Unsupported truth-check type.", check_type))
            continue
        try:
            passed, metrics = checker(check, root)
            results.append(
                {
                    "id": identifier,
                    "family": check.get("family"),
                    "type": check_type,
                    "status": "PASS" if passed else "FAIL",
                    "metrics": metrics,
                }
            )
            if not passed:
                findings.append(
                    finding("Critical", "TRUTH_CHECK_FAILED", f"Independent check failed: {identifier}", metrics)
                )
        except Exception as exc:
            results.append(
                {
                    "id": identifier,
                    "family": check.get("family"),
                    "type": check_type,
                    "status": "ERROR",
                    "error": str(exc),
                }
            )
            findings.append(finding("Blocker", "TRUTH_CHECK_ERROR", f"{identifier}: {exc}"))
    passed_count = sum(item["status"] == "PASS" for item in results)
    return {
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
        },
        "checks": results,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        root = (args.root or args.manifest.parent).resolve()
        report = inspect(payload, root)
    except Exception as exc:
        report = {
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "checks": [],
            "findings": [finding("Blocker", "MANIFEST_READ", str(exc))],
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
