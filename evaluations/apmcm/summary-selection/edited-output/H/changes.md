# Changes — case H

Deletions/merges only; no facts added.

- Deleted the raw input vectors X = (9, 3), Y = (6, 8), Z = (5, 2): given inputs, encoded by the score functions and retained in the body.
- Deleted the formula S_Z = 2 + 3w: Z's outcome is fully carried by the retained answer "Z is strictly dominated by X and never wins" (and "remains dominated throughout" in Q3).
- Deleted the tie score "6.75" at w = 5/8: Q2 requires the tie location, not the score level there; the value is derivable in the body.
- Deleted the derivation chain "d = a_X − a_Y ranges over [1, 5] and S_X − S_Y = w(d + 5) − 5", keeping the resulting worst-case interval [6w − 5, 10w − 5] that directly yields the robust regions; the corner arithmetic stays in the body.
- Merged the weak-guarantee explanation into one clause; kept the boundary-tie nuance (it qualifies the meaning of "guaranteed no worse").

Retained: Q1 answer (Y unique at w = 0.4, with all three scores); Q2 complete winner function including the tie (Y: 0 ≤ w < 5/8; tie at 5/8; X: 5/8 < w ≤ 1; Z never wins); Q3 perturbation ranges, worst-case interval, robust regions (Y ≤ 1/2, X ≥ 5/6, middle conditional), boundary-tie qualification, and Z remaining dominated; the non-probability scope boundary.
