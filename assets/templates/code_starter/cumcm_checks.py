"""Small, dependency-light checks for CUMCM solver verification scripts.

Copy this file into the project. Keep verification code separate from the
solver so the same bug is less likely to generate and validate a result.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping


def _finite_numbers(values: Iterable[float]) -> list[float]:
    numbers = [float(value) for value in values]
    if not numbers or not all(math.isfinite(value) for value in numbers):
        raise ValueError("expected a nonempty sequence of finite numbers")
    return numbers


@dataclass
class VerificationReport:
    checks: list[dict] = field(default_factory=list)

    def add(self, check_id: str, passed: bool, message: str, evidence=None) -> None:
        item = {
            "id": str(check_id),
            "passed": bool(passed),
            "message": str(message),
        }
        if evidence is not None:
            item["evidence"] = evidence
        self.checks.append(item)

    @property
    def passed(self) -> bool:
        return bool(self.checks) and all(item["passed"] for item in self.checks)

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {"result": "PASS" if self.passed else "FAIL", "checks": self.checks}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def print_marker(self) -> None:
        print(f"RESULT: {'PASS' if self.passed else 'FAIL'}")


def check_finite(report: VerificationReport, check_id: str, values: Iterable[float]) -> None:
    try:
        numbers = _finite_numbers(values)
        report.add(check_id, True, "All values are finite.", {"count": len(numbers)})
    except Exception as exc:
        report.add(check_id, False, "Non-finite or empty result detected.", str(exc))


def check_bounds(
    report: VerificationReport,
    check_id: str,
    values: Iterable[float],
    lower: float | None = None,
    upper: float | None = None,
    tolerance: float = 0.0,
) -> None:
    try:
        numbers = _finite_numbers(values)
        violations = []
        for index, value in enumerate(numbers):
            if lower is not None and value < float(lower) - tolerance:
                violations.append({"index": index, "value": value, "bound": "lower"})
            if upper is not None and value > float(upper) + tolerance:
                violations.append({"index": index, "value": value, "bound": "upper"})
        report.add(
            check_id,
            not violations,
            "Bounds satisfied." if not violations else "Bound violations detected.",
            {"minimum": min(numbers), "maximum": max(numbers), "violations": violations[:20]},
        )
    except Exception as exc:
        report.add(check_id, False, "Could not evaluate bounds.", str(exc))


def check_residuals(
    report: VerificationReport,
    check_id: str,
    residuals: Mapping[str, float],
    tolerance: float,
) -> None:
    try:
        normalized = {str(key): abs(float(value)) for key, value in residuals.items()}
        if not normalized or not all(math.isfinite(value) for value in normalized.values()):
            raise ValueError("residuals must be nonempty and finite")
        failed = {key: value for key, value in normalized.items() if value > tolerance}
        report.add(
            check_id,
            not failed,
            "Residual tolerance satisfied." if not failed else "Residual tolerance exceeded.",
            {"tolerance": tolerance, "maximum": max(normalized.values()), "failed": failed},
        )
    except Exception as exc:
        report.add(check_id, False, "Could not evaluate residuals.", str(exc))


def check_close(
    report: VerificationReport,
    check_id: str,
    actual: float,
    expected: float,
    absolute_tolerance: float = 0.0,
    relative_tolerance: float = 0.0,
) -> None:
    actual_value = float(actual)
    expected_value = float(expected)
    allowed = max(
        float(absolute_tolerance),
        float(relative_tolerance) * max(abs(actual_value), abs(expected_value)),
    )
    error = abs(actual_value - expected_value)
    report.add(
        check_id,
        math.isfinite(error) and error <= allowed,
        "Values agree within tolerance." if error <= allowed else "Values disagree.",
        {"actual": actual_value, "expected": expected_value, "error": error, "allowed": allowed},
    )
