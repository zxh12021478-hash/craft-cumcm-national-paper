# Note for case H

## Key claims and their locations
- Q1 scores at w = 0.4: X 5.4 (27/5), Y 7.2 (36/5), Z 3.2 (16/5), winner Y: paper "Q1: fixed preference"; results.json `fixed_weight`, `scores`, `winner`; solve.py lines 5–8.
- Q2 score functions, tie at 5/8 = 0.625 with score 6.75, Y/X regions: paper "Q2: nominal weight regions"; results.json `nominal_tie_weight = 5/8`; algebra S_X − S_Y = 8w − 5 (solve.py line 10 comment).
- Z strictly dominated by X on both criteria, never a maximizer: paper "Q2: nominal weight regions"; results.json `Z_dominated = true`.
- Q3 robust regions: Y no worse for w ≤ 1/2, X no worse for w ≥ 5/6, middle conditional: paper "Q3: joint bounded perturbations"; results.json `robust_Y_no_worse_max_weight`, `robust_X_no_worse_min_weight`, `middle_region`; bounds derived from S_X − S_Y = w(d+5) − 5 with d ∈ [1,5].
- Boundary ties possible (weak optimality): paper "Q3: joint bounded perturbations"; results.json `boundary_ties_possible = true`.
- Scope (exact interval inequalities, not probabilities): paper "Conclusion and scope"; results.json `scope`.

## What was removed vs the original Summary
- The four corner differences listed as 1, 3, 3, 5 (derivation detail retained in the body; the interval [1,5] is kept).
- The explicit statement that no scaling, fitted weights or sampled weight grid is used (method discipline belonging to the body "Model" section).
- Redundant restatement of the non-probability caveat and the Z-dominance claim; each appears once in the new version.

## Unverified / out of scope
- Perturbation intervals are set constraints, not a probability law; robust regions are not reliability probabilities, and interval bounds are not confidence intervals (paper "Q3", "Conclusion and scope"; problem statement).
- Results are exact analytic inequalities for the finite three-option, bounded-input problem; no real measurements or preferences are validated (results.json `scope`).
- No new results were added; fractions and regions agree with results.json, which solve.py regenerates with assertions on the winner and corner differences.
