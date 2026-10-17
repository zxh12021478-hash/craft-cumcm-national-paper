"""Reproduce a small synthetic audit with Python's standard library only."""
import json
import runpy
from pathlib import Path

root = Path(__file__).resolve().parent
candidate = runpy.run_path(str(root / "solver-before.py"))["solve"]()
assert candidate == {"a": 8, "b": 2, "cost": 26}, "Demo input changed"
feasible = [
    {"a": a, "b": b, "cost": 2 * a + 5 * b}
    for a in range(7) for b in range(11) if a + b == 10
]
optimal = min(feasible, key=lambda p: p["cost"])
assert optimal == {"a": 6, "b": 4, "cost": 32}
baseline_cost = 2 * 4 + 5 * 6
result = {
    "case_type": "synthetic demonstration, not a contest benchmark",
    "original_program_output": candidate,
    "capacity_violation": {"warehouse": "A", "capacity": 6, "allocated": candidate["a"]},
    "paper_claimed_cost": 24,
    "recomputed_candidate_cost": candidate["cost"],
    "baseline_cost": baseline_cost,
    "paper_claimed_reduction_percent": 40,
    "candidate_arithmetic_reduction_percent": round((baseline_cost - candidate["cost"]) / baseline_cost * 100, 4),
    "candidate_reduction_is_valid": False,
    "enumerated_feasible_plans": len(feasible),
    "verified_optimum": optimal,
    "verified_reduction_percent": round((baseline_cost - optimal["cost"]) / baseline_cost * 100, 4),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
