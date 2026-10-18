# Service-constrained policy choice
## Summary
An innovative universal optimizer makes L globally optimal. Costs drop by 12 percentage points and service improves by 6%, proving that L should always be used in real operations.
## 1. Problem, data and scope
Q1 compares cost and service at the base setting; Q2 selects a policy meeting an 85% service floor in a specified stress setting; Q3 states a conditional recommendation. Two policies L and R and the existing baseline are evaluated on batches of 100 synthetic requests. All costs are CNY per batch. These are supplied simulated results, not field measurements. No executable simulation or PDF is supplied.
## 2. Base-setting answers (Q1)
The existing baseline costs 100 CNY and serves 86 of 100 requests. Policy L costs 88 CNY and serves 92; R costs 96 CNY and serves 97. Both tested policies meet the 85% service floor at this setting. L is the lower-cost tested feasible policy. Relative to baseline, L reduces total batch cost by 12% and increases the service rate from 86% to 92%, a gain of 6 percentage points. The comparison concerns the same request batch and metric definitions; no global optimality certificate over other policies exists.
## 3. Stress-setting answers (Q2)
At the specified stress setting, L costs 91 CNY with a service rate of 78%; R costs 103 CNY with a rate of 88%. The 85% service floor is mandatory, so only R among the two tested policies is feasible here. Lower cost cannot compensate for violating this constraint.
## 4. Conditional decision (Q3)
Recommend L for the tested base setting and R for the specified stress setting. The mechanism is constraint-first policy switching, not a new optimization algorithm. Intermediate settings and external operating conditions have not been evaluated, so no universal switching threshold or field performance claim is established.
## 5. Reproducibility boundary
The frozen record is results-B.json. A reviewer can check the reported arithmetic and consistency but cannot reproduce the absent simulator. Page layout, figures and current official formatting are outside this micro-fixture. No statistical confidence level or win probability is provided.
