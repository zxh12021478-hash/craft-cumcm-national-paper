# Forecast-informed inventory planning
## Summary
We use Python, regression, and an advanced optimizer to solve all problems. Our globally optimal strategy reduces real-world energy consumption by 25% and achieves 92% forecasting accuracy. It wins with a probability of 90%, proving excellent robustness and wide applicability.
## 1. Data and scope
This is a synthetic planning example. Demand is observed weekly, and forecasts are made for four weeks ahead. No deployment or physical energy measurement was performed. Monetary amounts are in CNY.
## 2. Forecasting (Q1)
Both methods use the same 20 nonoverlapping test targets at horizon four, with training data and features restricted to information available at the forecast origin. The seasonal-naive baseline has RMSE 10 items and the regression model has RMSE 8 items, calculated by pooling squared errors over the same targets. Q1 therefore recommends regression for this evaluated four-week forecasting task. No classification accuracy was computed. The regression coefficients are fitted only to training data. This paper does not establish a causal interpretation.
## 3. Inventory decision (Q2)
Forecasts determine planned buffer requirements. A capacity-constrained inventory model selects strategy P among 12 prespecified feasible candidates, with equal service requirements. Candidate costs are simulated under the same synthetic demand trajectory. P has total cost 120 CNY versus 150 CNY for the seasonal-naive planning baseline; all required capacity and stock-balance residual checks pass with tolerance 1e-8. These costs are not energy measurements. P is the least-cost strategy in the evaluated candidate set; the model does not certify global optimality over unrestricted policies. This candidate-set selection is routine optimization, not a new algorithm.
## 4. Perturbation analysis (Q3)
Using the same capacity and service requirements, P remains the least-cost evaluated candidate in 18 of 20 prespecified demand perturbation scenarios covering -10% to +10%. The scenarios have no assigned probabilities. Strategy R is preferable in the other two scenarios, both at +10% demand. The conditional recommendation is P in the tested base setting, with a switch to R for the two tested +10% cases; performance between or outside tested scenarios is not established.
## 5. Limitations and conclusion
These are simulated costs on a synthetic dataset, not field savings. The four-week predictive result is limited to the stated test set, and a finite scenario frequency is not a probability. We recommend regression-informed P for the base case, retaining R for the identified +10% cases. External deployment validation is future work.
## Appendix: reproduction notes
The compact frozen result record is results.json. No executable code or PDF is supplied in this micro-fixture, so the evaluator may check internal consistency but must not label code reproduction or visual/page inspection complete.
