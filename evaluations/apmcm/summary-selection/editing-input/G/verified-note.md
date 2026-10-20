# Note for case G

## Key claims and their locations
- Model and solution form C dT/dt = −h(T−Ta), k = h/C: paper "Model and data"; problem statement.
- Q1 non-identifiability, only k = 0.25 h⁻¹: paper "Q1: identifiable rate, not separate parameters"; results.json `rate_per_hour = 0.25`, `transient_separately_identifies_h_C = false`; solve.py line 9 (zero-intercept log-linear fit).
- Q2 h = 5 W/K, C = 20 Wh/K = 72,000 J/K: paper "Q2: independent scale information"; results.json `conductance_W_per_K`, `capacitance_Wh_per_K`, `capacitance_J_per_K`; solve.py lines 10–11.
- Q3 t = 3.67 h, 3-hour deadline not met: paper "Q3: deadline decision"; results.json `time_hours = 3.66516…`, `meets_3_hour_deadline = false`; solve.py line 12.
- Tangent value 2.4 h and why it reverses the decision: paper "Q3: deadline decision"; results.json `tangent_hours = 2.4`; solve.py line 13.
- Synthetic/no-validation scope: paper "Conclusion and limitations"; results.json `scope`; problem statement.

## What was removed vs the original Summary
- The four raw observations with full floating-point temperatures (input data, retained in the body and data.json).
- The illustrative pair (h,C) = (2.5,10) vs (5,20); the non-identifiability mechanism (joint rescaling) is stated without the worked duplicate pair, which stays in the body.
- Repeated unit explanations and the second full restatement of the limits; one shared scope sentence is retained.
- The tangent counterexample is kept (one clause) because it changes the deadline decision and is reported in the body; only the duplicated slope arithmetic was removed.

## Unverified / out of scope
- Data were generated exactly from k = 0.25 with no measurement-error model; zero residual is not validation (paper "Model and data", "Q1").
- No confidence interval is available; no physical accuracy, heat-loss, spatial or real-device claims (paper "Conclusion and limitations"; results.json `scope`).
- No new results were added; all numbers match results.json produced by solve.py from data.json.
