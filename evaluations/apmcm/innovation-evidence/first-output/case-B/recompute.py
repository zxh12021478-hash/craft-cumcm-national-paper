#!/usr/bin/env python3
"""Case-B local recomputation.

Scope: internal consistency check of the supplied fixture runs.csv ONLY.
It does NOT verify the absent implementation, the freeze process, or
equation fidelity; it is not field validation. The evaluation units are
the 12 days, not the 12,000 within-day requests.

Input (immutable):
  ../../input/case-B/runs.csv (relative to this script's directory)
Output:
  results.json next to this script.
"""
import csv
import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.abspath(os.path.join(HERE, "..", "..", "input", "case-B", "runs.csv"))
OUTPUT = os.path.join(HERE, "results.json")

POLICIES = ["P", "R"]
SERVICE_FLOOR = 0.90


def main():
    rows = []
    with open(INPUT, newline="") as f:
        for r in csv.DictReader(f):
            for k in ("requests", "served", "complete", "hard_feasible", "cost_complete"):
                r[k] = int(r[k])
            r["cost_cny"] = float(r["cost_cny"])
            r["service_rate"] = r["served"] / r["requests"]
            rows.append(r)

    by_day = defaultdict(dict)
    for r in rows:
        by_day[r["day"]][r["policy"]] = r

    per_policy = {}
    for p in POLICIES:
        prows = [by_day[d][p] for d in sorted(by_day)]
        per_policy[p] = {
            "days": len(prows),
            "total_requests": sum(r["requests"] for r in prows),
            "total_served": sum(r["served"] for r in prows),
            "aggregate_service_rate": sum(r["served"] for r in prows)
            / sum(r["requests"] for r in prows),
            "min_daily_service_rate": min(r["service_rate"] for r in prows),
            "max_daily_service_rate": max(r["service_rate"] for r in prows),
            "total_cost": sum(r["cost_cny"] for r in prows),
            "all_complete": all(r["complete"] == 1 for r in prows),
            "all_hard_feasible": all(r["hard_feasible"] == 1 for r in prows),
            "all_cost_complete": all(r["cost_complete"] == 1 for r in prows),
            "days_below_90pct_floor": [r["day"] for r in prows if r["service_rate"] < SERVICE_FLOOR],
        }

    # paired day-level differences (R - P); negative cost diff favors R
    cost_diffs = [by_day[d]["R"]["cost_cny"] - by_day[d]["P"]["cost_cny"]
                  for d in sorted(by_day)]
    served_diffs = [by_day[d]["R"]["served"] - by_day[d]["P"]["served"]
                    for d in sorted(by_day)]
    paired = {
        "units": "days (n=12); requests within a day are not independent replications",
        "cost_difference_R_minus_P": cost_diffs,
        "served_difference_R_minus_P": served_diffs,
        "days_R_cost_favored": sum(1 for x in cost_diffs if x < 0),
        "days_R_service_favored": sum(1 for x in served_diffs if x > 0),
        "mean_daily_cost_diff": statistics.mean(cost_diffs),
        "sd_daily_cost_diff": statistics.pstdev(cost_diffs),
        "note": "zero variance -> t-statistic/CI degenerate; paper makes no significance claim",
    }

    totals = {
        "P_total_cost": per_policy["P"]["total_cost"],
        "R_total_cost": per_policy["R"]["total_cost"],
        "cost_reduction_relative_to_P": (per_policy["P"]["total_cost"] - per_policy["R"]["total_cost"])
        / per_policy["P"]["total_cost"],
        "P_aggregate_service_rate": per_policy["P"]["aggregate_service_rate"],
        "R_aggregate_service_rate": per_policy["R"]["aggregate_service_rate"],
        "service_gain_percentage_points": (per_policy["R"]["aggregate_service_rate"]
                                           - per_policy["P"]["aggregate_service_rate"]) * 100,
        "both_meet_90pct_floor_every_day": (
            not per_policy["P"]["days_below_90pct_floor"]
            and not per_policy["R"]["days_below_90pct_floor"]
        ),
    }

    results = {
        "input_file": INPUT,
        "check_scope": "fixture internal consistency only; not implementation or freeze-process verification",
        "per_policy": per_policy,
        "paired_day_level": paired,
        "headline_totals": totals,
    }

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"days: {len(by_day)}")
    for p in POLICIES:
        pp = per_policy[p]
        print(f"{p}: cost {pp['total_cost']:.0f}, served {pp['total_served']}/{pp['total_requests']} "
              f"= {pp['aggregate_service_rate']:.2%}, daily min {pp['min_daily_service_rate']:.2%}, "
              f"complete={pp['all_complete']} feasible={pp['all_hard_feasible']}")
    print(f"cost reduction vs P: {totals['cost_reduction_relative_to_P']:.4f}; "
          f"service gain: {totals['service_gain_percentage_points']:.1f} pp; "
          f"floor ok: {totals['both_meet_90pct_floor_every_day']}")
    print(f"R cost-favored days: {paired['days_R_cost_favored']}/12")
    print(f"results -> {OUTPUT}")


if __name__ == "__main__":
    main()
