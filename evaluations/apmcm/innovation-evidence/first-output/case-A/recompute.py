#!/usr/bin/env python3
"""Case-A local recomputation.

Scope: internal consistency check of the supplied fixture runs.csv ONLY.
It does NOT verify the absent dispatch implementation or equation fidelity,
and it is NOT an empirical/held-out validation.

Input (immutable):
  ../../input/case-A/runs.csv (relative to this script's directory)
Output:
  results.json next to this script.
"""
import csv
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.abspath(os.path.join(HERE, "..", "..", "input", "case-A", "runs.csv"))
OUTPUT = os.path.join(HERE, "results.json")

POLICIES = ["B", "T", "TM"]
GROUPS = ["quiet", "peak", "boundary"]


def pct_change(base, cand):
    """Relative saving of cand vs base: (base - cand)/base. Negative = cand is more expensive."""
    return (base - cand) / base if base else None


def main():
    rows = []
    with open(INPUT, newline="") as f:
        for r in csv.DictReader(f):
            r["complete"] = int(r["complete"])
            r["hard_feasible"] = int(r["hard_feasible"])
            r["cost_complete"] = int(r["cost_complete"])
            r["cost_cny"] = float(r["cost_cny"])
            rows.append(r)

    # index by scenario and policy
    by_scenario = defaultdict(dict)
    group_of = {}
    for r in rows:
        by_scenario[r["scenario"]][r["policy"]] = r
        group_of[r["scenario"]] = r["group"]

    # ---- per-policy feasibility / cost accounting ----
    per_policy = {}
    for p in POLICIES:
        prows = [r for r in rows if r["policy"] == p]
        valid = [r for r in prows if r["complete"] == 1 and r["hard_feasible"] == 1]
        per_policy[p] = {
            "runs": len(prows),
            "complete": sum(r["complete"] for r in prows),
            "hard_feasible": sum(r["hard_feasible"] for r in prows),
            "complete_and_feasible": len(valid),
            "feasibility_rate": len(valid) / len(prows),
            "logged_cost_sum_all_rows": sum(r["cost_cny"] for r in prows),
            "complete_cost_sum": sum(r["cost_cny"] for r in prows if r["cost_complete"] == 1),
            "incomplete_logged_costs": {
                r["scenario"]: r["cost_cny"] for r in prows if r["cost_complete"] == 0
            },
        }

    pooled_pass = sum(per_policy[p]["complete_and_feasible"] for p in POLICIES)
    pooled_runs = sum(per_policy[p]["runs"] for p in POLICIES)

    # ---- group x policy breakdown (complete costs only; incomplete flagged) ----
    group_breakdown = {}
    for g in GROUPS:
        group_breakdown[g] = {}
        scenarios = [s for s, gg in group_of.items() if gg == g]
        for p in POLICIES:
            prows = [by_scenario[s][p] for s in scenarios]
            valid = [r for r in prows if r["complete"] == 1 and r["hard_feasible"] == 1]
            group_breakdown[g][p] = {
                "scenarios": len(scenarios),
                "complete_and_feasible": len(valid),
                "complete_cost_sum": sum(r["cost_cny"] for r in prows if r["cost_complete"] == 1),
                "logged_cost_incomplete_sum": sum(
                    r["cost_cny"] for r in prows if r["cost_complete"] == 0
                ),
            }

    # ---- paired comparisons on the intersection of scenarios where BOTH are valid ----
    def paired(base_p, cand_p):
        common = [
            s for s in by_scenario
            if by_scenario[s][base_p]["complete"] == 1
            and by_scenario[s][base_p]["hard_feasible"] == 1
            and by_scenario[s][cand_p]["complete"] == 1
            and by_scenario[s][cand_p]["hard_feasible"] == 1
        ]
        base_cost = sum(by_scenario[s][base_p]["cost_cny"] for s in common)
        cand_cost = sum(by_scenario[s][cand_p]["cost_cny"] for s in common)
        return {
            "common_valid_scenarios": len(common),
            "common_scenario_ids": sorted(common),
            "base_cost": base_cost,
            "candidate_cost": cand_cost,
            "candidate_relative_saving": pct_change(base_cost, cand_cost),
        }

    comparisons = {
        "B_vs_T": paired("B", "T"),
        "B_vs_TM": paired("B", "TM"),
        "T_vs_TM": paired("T", "TM"),
    }

    # ---- headline claims from the paper ----
    claim_checks = {
        "claimed_quiet_20pct_saving": {
            "quiet_B_complete_cost": group_breakdown["quiet"]["B"]["complete_cost_sum"],
            "quiet_TM_complete_cost": group_breakdown["quiet"]["TM"]["complete_cost_sum"],
            "quiet_TM_vs_B_saving": pct_change(
                group_breakdown["quiet"]["B"]["complete_cost_sum"],
                group_breakdown["quiet"]["TM"]["complete_cost_sum"],
            ),
            "scope": "arithmetic valid for the 8 quiet scenarios only; not an overall result",
        },
        "claimed_peak_table": {
            "peak_B_complete_cost": group_breakdown["peak"]["B"]["complete_cost_sum"],
            "peak_TM_complete_cost": group_breakdown["peak"]["TM"]["complete_cost_sum"],
            "peak_TM_vs_B_saving": pct_change(
                group_breakdown["peak"]["B"]["complete_cost_sum"],
                group_breakdown["peak"]["TM"]["complete_cost_sum"],
            ),
        },
        "claimed_reliability_90pct": {
            "TM_feasibility_rate": per_policy["TM"]["feasibility_rate"],
            "pooled_feasibility_rate": pooled_pass / pooled_runs,
            "matches_90pct_for_TM": abs(per_policy["TM"]["feasibility_rate"] - 0.90) < 1e-9,
            "matches_90pct_pooled": abs(pooled_pass / pooled_runs - 0.90) < 1e-9,
        },
        "boundary_group": {
            "B_complete_cost": group_breakdown["boundary"]["B"]["complete_cost_sum"],
            "T_complete_cost": group_breakdown["boundary"]["T"]["complete_cost_sum"],
            "TM_valid_runs": group_breakdown["boundary"]["TM"]["complete_and_feasible"],
            "TM_logged_partial_cost": group_breakdown["boundary"]["TM"]["logged_cost_incomplete_sum"],
        },
    }

    results = {
        "input_file": INPUT,
        "check_scope": "fixture internal consistency only; not implementation verification, not held-out validation",
        "n_scenarios": len(by_scenario),
        "per_policy": per_policy,
        "pooled_feasibility": {"pass_runs": pooled_pass, "total_runs": pooled_runs,
                               "rate": pooled_pass / pooled_runs},
        "group_breakdown": group_breakdown,
        "paired_comparisons_on_common_valid_scenarios": comparisons,
        "paper_claim_checks": claim_checks,
    }

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # compact console summary
    print(f"scenarios: {len(by_scenario)}")
    for p in POLICIES:
        pp = per_policy[p]
        print(f"{p}: feasible {pp['complete_and_feasible']}/{pp['runs']} "
              f"({pp['feasibility_rate']:.1%}), complete-cost sum {pp['complete_cost_sum']:.0f}, "
              f"logged-all sum {pp['logged_cost_sum_all_rows']:.0f}")
    print(f"pooled feasibility: {pooled_pass}/{pooled_runs} = {pooled_pass/pooled_runs:.4f}")
    for k, v in comparisons.items():
        print(f"{k}: n={v['common_valid_scenarios']} base={v['base_cost']:.0f} "
              f"cand={v['candidate_cost']:.0f} saving={v['candidate_relative_saving']:.4f}")
    print(f"results -> {OUTPUT}")


if __name__ == "__main__":
    main()
