# Note for case F

## Key claims and their locations
- Feasibility rule `s/100 >= 0.90 and d <= 6`, exhaustive cost comparison: paper "Model and method"; solve.py lines 8–9; results.json `base.feasible`, `stress.feasible`.
- Q1: B chosen, CNY 210, 95 served, 5.0 h: paper "Base results (Q1)"; results.json `base.chosen`; data.json `base`.
- 12.5% saving vs reference A: paper "Base results (Q1)" `(240-210)/240 = 12.5%`; results.json `base.saving_vs_A = 0.125`; solve.py line 11.
- C cheaper but infeasible on time (7.0 h > 6): paper "Base results (Q1)"; data.json base row C.
- Q2: D sole feasible stress policy, CNY 255, 94 served, 5.7 h: paper "Stress results (Q2)"; results.json `stress.feasible = ["D"]`, `stress.chosen`.
- B fails stress at 84%: paper "Stress results (Q2)"; data.json stress row B.
- Scenario-qualified recommendation and limits: paper "Conclusion and limits"; results.json `scope`.

## What was removed vs the original Summary
- Full per-policy rows for both batches (all ten cost/served/time triples); they remain in the two body tables.
- Redundant restatement of units and denominators already fixed in the body.
- The closing checklist of things not asserted (no confidence intervals, probabilities, etc.), folded into one scope-qualified sentence; only the limits that change interpretation (five tested policies, synthetic tables, no deployment validity) are kept.

## Unverified / out of scope
- No controller implementation or field data exists; the script screens the supplied table only (paper "Model and method"; results.json `scope`).
- No distribution links the two batches; no claim about all possible policies or future batches (problem statement).
- No new results were added; every number traces to data.json/results.json and is reproduced by solve.py.
