#!/usr/bin/env python3
"""Independent recomputation for case-A.

Numeric cross-check only: reads the supplied runs.csv and rebuilds every
headline metric from the raw rows. No original implementation exists for
case-A, so this is not a program-reproduction check. All costs from runs
with cost_complete=0 are excluded from cost totals (they are partial logs
of invalid plans, not complete operating costs).
"""
import csv
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.normpath(os.path.join(HERE, "..", "..", "input", "case-A", "runs.csv"))


def pct_change(base, cand):
    """Relative change (cand - base) / base, baseline non-zero."""
    return (cand - base) / base if base else None


def main():
    rows = []
    with open(INPUT, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "scenario": r["scenario"],
                "group": r["group"],
                "policy": r["policy"],
                "complete": int(r["complete"]),
                "hard_feasible": int(r["hard_feasible"]),
                "cost": float(r["cost_cny"]),
                "cost_complete": int(r["cost_complete"]),
            })

    policies = ["B", "T", "TM"]
    groups = ["quiet", "peak", "boundary"]

    # ---- per policy x group aggregates ----
    cells = {}
    for p in policies:
        for g in groups:
            sub = [r for r in rows if r["policy"] == p and r["group"] == g]
            complete = [r for r in sub if r["cost_complete"] == 1]
            cells[f"{p}|{g}"] = {
                "n_scenarios": len(sub),
                "complete": sum(r["complete"] for r in sub),
                "hard_feasible": sum(r["hard_feasible"] for r in sub),
                "complete_cost_sum": sum(r["cost"] for r in complete),
                "complete_cost_mean": (sum(r["cost"] for r in complete) / len(complete))
                                      if complete else None,
                "partial_logged_cost_sum": sum(r["cost"] for r in sub
                                               if r["cost_complete"] == 0),
            }

    # ---- per policy overall ----
    overall = {}
    for p in policies:
        sub = [r for r in rows if r["policy"] == p]
        complete = [r for r in sub if r["cost_complete"] == 1]
        overall[p] = {
            "n_scenarios": len(sub),
            "complete": sum(r["complete"] for r in sub),
            "hard_feasible": sum(r["hard_feasible"] for r in sub),
            "feasible_share": sum(r["hard_feasible"] for r in sub) / len(sub),
            "valid_cost_sum": sum(r["cost"] for r in complete),
            "valid_cost_mean": sum(r["cost"] for r in complete) / len(complete)
                               if complete else None,
        }

    # ---- paired comparisons on scenarios where both runs complete ----
    by = {(r["scenario"], r["policy"]): r for r in rows}
    scenarios = sorted({r["scenario"] for r in rows})

    def paired(p1, p2):
        diffs = []
        for s in scenarios:
            a, b = by.get((s, p1)), by.get((s, p2))
            if a and b and a["cost_complete"] == 1 and b["cost_complete"] == 1:
                diffs.append({"scenario": s, "group": a["group"],
                              f"{p1}_cost": a["cost"], f"{p2}_cost": b["cost"],
                              f"diff_{p2}_minus_{p1}": b["cost"] - a["cost"]})
        key = f"diff_{p2}_minus_{p1}"
        return {
            "n_paired": len(diffs),
            "sum_" + p1: sum(d[f"{p1}_cost"] for d in diffs),
            "sum_" + p2: sum(d[f"{p2}_cost"] for d in diffs),
            "n_favoring_" + p2: sum(1 for d in diffs if d[key] < 0),
            "n_favoring_" + p1: sum(1 for d in diffs if d[key] > 0),
            "n_ties": sum(1 for d in diffs if d[key] == 0),
            "relative_change_vs_" + p1: pct_change(
                sum(d[f"{p1}_cost"] for d in diffs),
                sum(d[f"{p2}_cost"] for d in diffs)),
            "rows": diffs,
        }

    pairs = {
        "T_vs_B": paired("B", "T"),
        "TM_vs_T": paired("T", "TM"),
        "TM_vs_B": paired("B", "TM"),
    }

    # ---- explicit checks of the paper's headline claims ----
    quiet = {p: cells[f"{p}|quiet"] for p in policies}
    peak = {p: cells[f"{p}|peak"] for p in policies}
    boundary = {p: cells[f"{p}|boundary"] for p in policies}

    claims = {
        "quiet_only_saving_TM_vs_B": {
            "B_sum": quiet["B"]["complete_cost_sum"],
            "TM_sum": quiet["TM"]["complete_cost_sum"],
            "saving": pct_change(quiet["B"]["complete_cost_sum"],
                                 quiet["TM"]["complete_cost_sum"]),
            "paper_quote": "-20% (20% saving)",
        },
        "peak_TM_vs_B": {
            "B_sum": peak["B"]["complete_cost_sum"],
            "TM_sum": peak["TM"]["complete_cost_sum"],
            "relative_change": pct_change(peak["B"]["complete_cost_sum"],
                                          peak["TM"]["complete_cost_sum"]),
        },
        "boundary_TM": {
            "complete": boundary["TM"]["complete"],
            "hard_feasible": boundary["TM"]["hard_feasible"],
            "partial_logged_cost_sum": boundary["TM"]["partial_logged_cost_sum"],
        },
        "reliability_share_on_set": {
            "B": overall["B"]["feasible_share"],
            "T": overall["T"]["feasible_share"],
            "TM": overall["TM"]["feasible_share"],
            "paper_abstract_reports_TM": 0.90,
        },
        "TM_aggregate_on_its_16_completed": {
            "B_sum": pairs["TM_vs_B"]["sum_B"],
            "T_sum": pairs["TM_vs_T"]["sum_T"],
            "TM_sum": pairs["TM_vs_B"]["sum_TM"],
            "TM_vs_B_relative": pairs["TM_vs_B"]["relative_change_vs_B"],
            "TM_vs_T_relative": pairs["TM_vs_T"]["relative_change_vs_T"],
        },
        "full_fixture_valid_totals": {
            "B": overall["B"]["valid_cost_sum"],
            "T": overall["T"]["valid_cost_sum"],
            "TM": "not definable: 4 infeasible plans (partial costs only)",
        },
    }

    out = {
        "source": os.path.relpath(INPUT, HERE),
        "n_scenarios": len(scenarios),
        "group_membership": {g: sorted({r["scenario"] for r in rows if r["group"] == g})
                             for g in groups},
        "cells": cells,
        "overall": overall,
        "paired": pairs,
        "claim_checks": claims,
    }

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("overall", "claim_checks")}, indent=2))


if __name__ == "__main__":
    main()
