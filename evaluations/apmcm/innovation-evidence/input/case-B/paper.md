# A frozen dispatch refinement evaluated on separate synthetic days

## Task
Choose between reference P and refinement R on the provided evaluation days. Both must satisfy the specified inventory and supply constraints, serve at least 90% of requests on each evaluation day, and then minimize complete operating cost. The mechanism in R changes the timing of a reserve release. No real deployment or prize-related claim is requested.

## Summary
A reserve-release refinement reduced total operating cost by 5%, from CNY 12,000 to 11,400, across twelve held-out synthetic days. Service rose from 94% to 96%, a gain of 2 percentage points, and both policies met the 90% daily service floor and all recorded hard constraints. R is therefore recommended over P for this tested set. Generalization beyond the synthetic generator and real implementation remain unverified.

## Method and scope
P and R were each tuned over six configurations on thirty different synthetic development days. Both received the same feature history, tuning-evaluation count, stopping rules and cost definition. A log records that both configurations were frozen before the twelve evaluation days were generated. Evaluation days were not subsequently used to tune or select configurations. Paired rows correspond to the same day and inputs. All costs cover the complete day and include the same cost components. Results are supplied as a fixture; no source implementation is available for checking equations. Each day has 1,000 requests; requests within a day share demand conditions, and the twelve days are the evaluation units. This is a comparison of two tested policies, not a global-optimality proof or a formal attribution of every gain to an isolated mechanism.

## Results
The full results table is supplied in runs.csv, with twelve daily pairs. P costs CNY 1,000 and serves 940 of 1,000 requests each day. R costs CNY 950 and serves 960 each day. Both have twelve complete and recorded-feasible runs. Total costs are therefore CNY 12,000 and 11,400; the reduction relative to P is 5%. Aggregate service is 94% and 96%, respectively, a gain of 2 percentage points. Every daily service rate exceeds the required 90%. No confidence interval, test of significance, probability of future feasibility or field-performance claim is made. All twelve paired cost differences favor R; that does not make the 12,000 requests independent replications.

## Conclusion
Choose R over P for these twelve held-out synthetic days. The table supports the stated cost and service comparison, subject to the supplied fixture. It does not establish unseen demand coverage, a universal best controller or hardware performance. R's exact mechanism and equation fidelity should be reviewed from the actual implementation if it becomes available. We do not need a larger experiment to report this limited descriptive comparison honestly.
