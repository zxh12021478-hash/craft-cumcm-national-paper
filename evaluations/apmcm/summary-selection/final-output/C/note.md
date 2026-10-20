# Note for case C

## Key claims and their locations
- Enumeration of all 2^3 = 8 subsets with integer recomputation: paper "Exact solution and proof"; solve.py lines 10–18.
- Four feasible designs (A+B 12, B+C 15, A+C 17, A+B+C 22): paper "Exact solution and proof"; results.json `candidates` (feasible flags).
- Q1 unique optimum A+B, CNY 12, normal supply 7: results.json `optimal_designs`; paper "Exact solution and proof".
- Reference B+C at CNY 15 and 20% reduction `(15−12)/15`: paper "Model and baseline", "Exact solution and proof"; results.json `reference`, `reference_cost_cny`, `cost_reduction = 0.2`.
- Q2 failure residuals: lose A → 3 (B), lose B → 4 (A): paper "Exact solution and proof", "Conclusion and limits"; results.json candidate A+B `single_failure_supply`.
- Scope: exact for the finite stipulated model, no hardware/probability claims: paper "Conclusion and limits"; results.json `scope`; problem statement.

## What was removed vs the original Summary
- Nothing material was missing from the original Summary; the new version removes the module capacity/cost input list (4,3,5 units/day; 7,5,10 CNY), which is given in the body and was not needed to recover either answer.
- The full per-candidate feasibility/cost list and the "exactly four designs" enumeration detail remain in the body; the summary keeps the coverage statement, the unique optimum, its value, the reference comparison, and both failure residuals.

## Unverified / out of scope
- Additive, lossless capacities and the finite contingency set are stipulated, not measured (problem statement; paper "Model and baseline").
- No hardware performance, failure probability law, or generalization to unspecified multiple failures (paper "Conclusion and limits"; results.json `scope`).
- No new results were added; the numbers are results.json values reproduced by solve.py.
