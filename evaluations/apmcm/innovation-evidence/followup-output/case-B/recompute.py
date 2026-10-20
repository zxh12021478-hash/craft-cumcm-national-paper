#!/usr/bin/env python3
"""Independent recomputation for case-B.

Numeric cross-check only: reads the supplied runs.csv and rebuilds every
headline metric from raw rows. The evaluation units are the twelve paired
days; individual requests are never treated as independent replications.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.normpath(os.path.join(HERE, "..", "..", "input", "case-B", "runs.csv"))
SERVICE_FLOOR = 0.90


def main():
    rows = []
    with open(INPUT, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "day": r["day"],
                "policy": r["policy"],
                "requests": int(r["requests"]),
                "served": int(r["served"]),
                "complete": int(r["complete"]),
                "hard_feasible": int(r["hard_feasible"]),
                "cost": float(r["cost_cny"]),
                "cost_complete": int(r["cost_complete"]),
            })

    days = sorted({r["day"] for r in rows})
    policies = ["P", "R"]
    by = {(r["day"], r["policy"]): r for r in rows}

    per_policy = {}
    for p in policies:
        sub = [r for r in rows if r["policy"] == p]
        total_req = sum(r["requests"] for r in sub)
        total_served = sum(r["served"] for r in sub)
        per_policy[p] = {
            "n_days": len(sub),
            "complete": sum(r["complete"] for r in sub),
            "hard_feasible": sum(r["hard_feasible"] for r in sub),
            "total_cost": sum(r["cost"] for r in sub),
            "mean_daily_cost": sum(r["cost"] for r in sub) / len(sub),
            "total_requests": total_req,
            "total_served": total_served,
            "aggregate_service_rate": total_served / total_req,
            "daily_service_min": min(r["served"] / r["requests"] for r in sub),
            "daily_service_max": max(r["served"] / r["requests"] for r in sub),
            "days_below_90pct_floor": sum(1 for r in sub
                                          if r["served"] / r["requests"] < SERVICE_FLOOR),
        }

    # paired day-level differences
    paired = []
    for d in days:
        p, r = by[(d, "P")], by[(d, "R")]
        paired.append({
            "day": d,
            "cost_P": p["cost"],
            "cost_R": r["cost"],
            "cost_diff_R_minus_P": r["cost"] - p["cost"],
            "served_P": p["served"],
            "served_R": r["served"],
            "served_diff_R_minus_P": r["served"] - p["served"],
            "both_complete_feasible": bool(p["complete"] and r["complete"]
                                           and p["hard_feasible"] and r["hard_feasible"]),
        })

    cost_red = (per_policy["P"]["total_cost"] - per_policy["R"]["total_cost"]) \
        / per_policy["P"]["total_cost"]
    svc_pp = (per_policy["R"]["aggregate_service_rate"]
              - per_policy["P"]["aggregate_service_rate"])

    claim_checks = {
        "cost_reduction_R_vs_P": cost_red,
        "paper_quote_cost_reduction": 0.05,
        "service_rate_P": per_policy["P"]["aggregate_service_rate"],
        "service_rate_R": per_policy["R"]["aggregate_service_rate"],
        "service_gain_percentage_points": svc_pp * 100,
        "paper_quote_service": "94% -> 96%, +2 pp",
        "all_days_complete_and_feasible": all(x["both_complete_feasible"] for x in paired),
        "all_days_above_floor": (per_policy["P"]["days_below_90pct_floor"] == 0
                                 and per_policy["R"]["days_below_90pct_floor"] == 0),
        "paired_days_favoring_R_cost": sum(1 for x in paired if x["cost_diff_R_minus_P"] < 0),
        "paired_days_favoring_R_service": sum(1 for x in paired if x["served_diff_R_minus_P"] > 0),
        "n_evaluation_units": len(days),
        "note": "days are the evaluation units; 12,000 requests are not independent replications",
    }

    out = {
        "source": os.path.relpath(INPUT, HERE),
        "per_policy": per_policy,
        "paired_days": paired,
        "claim_checks": claim_checks,
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(claim_checks, indent=2))


if __name__ == "__main__":
    main()
