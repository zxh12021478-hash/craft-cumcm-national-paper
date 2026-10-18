# Integrated Planning — Minimal Revised Draft (audit stage, NOT a complete paper or a submittable final)

> This is a sentence-level repair of the existing draft based on the independent audit.
> Numbers that can be corrected from the supplied data/code have been corrected;
> infeasible or unverified claims are withdrawn. Q3 out-of-sample evaluation,
> Q4 preference-conditional ranking and Q5 sensitivity analysis are **not executed**
> and are not fabricated here; they are listed as unresolved.
> Change log: Summary (all four headline claims corrected); Q1 (cost percentage,
> proxy definition); Q2 (battery equation convention, infeasibility certificate,
> "optimal" withdrawn, solar worst case stated); Q3 (leakage and validation claims
> withdrawn); Q4 (probability claim withdrawn); Q5 (marked not executed); Conclusion
> (replaced false closure with a status list).

## Summary
The temperature target is 25 °C. [Revised] Electrical energy use falls from 100 to 95 kWh, a **5%** reduction; the dimensionless normalized comfort objective falls from 0.50 to 0.40 (a 20% change in a proxy, not an energy saving). Operating cost falls from 100 to 80 CNY (20%). [Revised] Under the stated constraints (solar = 0 worst case) the three-hour dispatch instance is **infeasible**, so no feasible or optimal plan is reported. [Revised] Forecast results are not established: only a training R² of 0.99 exists, and no out-of-sample evaluation has been run. [Revised] Design B ranks first in 82 of 100 analyst-selected scenarios; this is a scenario win rate, **not** a probability, and no probability of being optimal is claimed. Q5 (±5% demand sensitivity) has not been performed.

## Q1
The normalized comfort objective (a dimensionless, normalized index with no energy unit; it is not electrical energy) falls from 0.50 to 0.40, a change of 20%. Electrical energy falls from 100 to 95 kWh, a reduction of 5%. Operating cost falls from 100 to 80 CNY, a reduction of 20% relative to the original cost. [Revised] The three quantities are distinct and are not substituted for one another.

## Q2
[Revised] Solar generation is zero (worst case). Define c_t as kWh drawn from the grid for charging and d_t as kWh delivered to the load by discharge; with both efficiencies 0.9 the stored energy is
E_t = E_{t-1} + 0.9 c_t − d_t / 0.9,
and the hourly balance (solar = 0) is g_t + d_t = load_t + c_t, with 0 ≤ g_t ≤ 5, 0 ≤ c_t, d_t ≤ 2, 0 ≤ E_t ≤ 3, E_0 = E_3 = 0.

The originally proposed plan (grid [5,5,5], charge [1,0,0], discharge [0,2,0]) is **infeasible**: under the corrected convention its stored-energy states are [0.9, −1.322, −1.322] kWh (negative storage after hour 2, and the terminal state is −1.322 rather than 0). The plan cannot be made feasible because the instance itself is infeasible:

- Aggregate bound: total load is 4+7+5 = 16 kWh, whereas the grid can supply at most 3×5 = 15 kWh over the three hours; the battery starts and ends empty and round-trip efficiency is 0.9² = 0.81, so it cannot create energy. Every plan requires Σg ≥ 16 kWh.
- Hour-2 bound: after serving hour-1 load, at most 1 kWh can be charged (g_1 ≤ 5), so E_1 ≤ 0.9 and at most 0.81 kWh can be delivered in hour 2; hour-2 supply is at most 5 + 0.81 = 5.81 < 7 kWh.

An independent LP confirms infeasibility at the grid cap of 5 under both terminal conventions. The earlier "solver reports optimal" status is withdrawn; it is contradicted by these checks. The underlying solver model and run log are unavailable, so the cause of the inconsistent status cannot be determined from this bundle.

Context for a possible relaxation (audit-side analysis, not part of the asked answer): relaxing only the grid cap, a uniform cap of G* = 1024/181 ≈ 5.65746 kWh is the smallest feasible value; the exact-checked plan is grid [1024/181, 1024/181, 5], charge [300/181, 0, 0], discharge [0, 243/181, 0], with stored energy [270/181, 0, 0] (exact zero residual). Relaxing battery capacity or charge/discharge rates cannot remove the 1 kWh aggregate deficit.

## Q3
[Revised] The reported forecasting results are withdrawn as evidence about future weeks.
- The feature `resolved_service_tickets` is finalized one week after the forecast target, so it is not in the information set at the forecast origin (feature availability guard: available_at 82 > origin 80 for the h=1 example). It must be removed or replaced by origin-available information (e.g. a lagged series whose release time satisfies available_at ≤ origin for every horizon).
- The four future promotion values were taken from realized records (available_at 83 > origin 80 for the h=3 example). Unknown future exogenous values must instead be declared scenarios formed at the origin (formed_at ≤ origin) or omitted; realized values cannot be relabeled as scenarios.
- A random 80/20 split across all dates is not a temporal out-of-sample test; rolling or expanding-origin backtests are required, with per-horizon errors.
- Training R² = 0.99 is an in-sample fit statistic only; it does not establish 99% future accuracy. **Genuine out-of-sample errors have not been computed (not executed / unverified).**

## Q4
[Revised] Design B ranks first in 82 of the 100 analyst-selected preference scenarios; this count is retained as a count. It is not a probability that B is optimal in real operation: the scenarios were analyst-selected, no probability model over the sponsor's unknown weights exists, and scenario win frequencies are not calibrated probabilities. The required preference-conditional ranking — dominance screening, the weight regions in which each design ranks first, and conditional recommendations — **has not been performed (not executed / unverified)**, and no unconditional unique winner is asserted.

## Q5
[Not executed] The sensitivity of the recommendation to −5% and +5% demand changes has not been quantified; no results, code or rerun outputs exist. It must be run in both directions on the corrected downstream models after Q2–Q4 are repaired, reporting any rank reversals and regret with the baseline centered.

## Conclusion
[Revised] The temperature target is 25 °C. The Q1 raw values are retained (comfort proxy 0.50→0.40; electrical energy 100→95 kWh, −5%; cost 100→80 CNY, −20%). The Q2 instance under the stated constraints is infeasible (certificate above), and the previously claimed feasible/optimal dispatch is withdrawn. Q3's future-performance claim is withdrawn and out-of-sample evaluation is not executed; Q4's 82% is a scenario win rate, not a probability, and preference-conditional ranking is not executed; Q5 is not executed. These items remain unresolved, so the draft cannot be presented as a complete answer.
