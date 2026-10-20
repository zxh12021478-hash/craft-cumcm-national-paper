# Dispatch selection with service and delivery constraints

## Summary
We consider a base batch and a stress batch, each with 100 requests, and compare five fixed policies called A, B, C, D and E. Complete operating cost is in CNY, the served fraction has denominator 100, and maximum delivery time is measured in hours only over served requests. The required service floor is 90% and the maximum-delivery-time limit is 6 hours in both scenarios. On the base batch policy A has cost 240, serves 92, and has maximum time 5.5; B has cost 210, serves 95, and has maximum time 5.0; C has cost 205, serves 96, and has maximum time 7.0; D has cost 230, serves 91, and has maximum time 4.5; and E has cost 260, serves 99, and has maximum time 6.0. Filtering policies against the service and time requirements and comparing full costs selects B for the base batch, at CNY 210 compared with A's CNY 240, a 12.5% saving. On the stress batch A has cost 250, serves 88, and takes 5.8 hours; B costs 225, serves 84, and takes 5.5; C costs 220, serves 87, and takes 8.0; D costs 255, serves 94, and takes 5.7; and E costs 280, serves 97, and takes 6.5. Thus D is the sole feasible stress policy. We recommend B for the base batch and D for the stress batch. The records do not show that B is optimal among all possible dispatch policies, that D will satisfy future constraints, or that the improvement is empirically validated in deployment. No confidence intervals, reliability probabilities or universal recommendation are asserted.

## Model and method
Each row is a complete policy run on a specified batch. Let cost c, served count s and maximum delivery time d be the recorded outputs. The feasible set is {policy: s/100 >= 0.90 and d <= 6}. We minimize c within that finite set, using exhaustive comparison rather than a fitted score that could compensate a constraint violation with low cost. The stress batch is not a random draw from a supplied distribution. No source implementation of the dispatch controllers or field measurements is available. The accompanying script independently screens the supplied table; it does not validate the controllers.

## Base results (Q1)
| Policy | Complete cost, CNY | Served / 100 | Maximum time, h |
|---|---:|---:|---:|
| A | 240 | 92 | 5.5 |
| B | 210 | 95 | 5.0 |
| C | 205 | 96 | 7.0 |
| D | 230 | 91 | 4.5 |
| E | 260 | 99 | 6.0 |

A, B, D and E meet both constraints. C is cheaper but violates the time limit and cannot be recommended. B is the least-cost feasible policy among the five tested, at CNY 210 versus CNY 240 for the defined reference A: (240-210)/240 = 12.5%. Its service is 95% and maximum time is 5.0 hours. These are table-based comparisons on the specified base batch.

## Stress results (Q2)
| Policy | Complete cost, CNY | Served / 100 | Maximum time, h |
|---|---:|---:|---:|
| A | 250 | 88 | 5.8 |
| B | 225 | 84 | 5.5 |
| C | 220 | 87 | 8.0 |
| D | 255 | 94 | 5.7 |
| E | 280 | 97 | 6.5 |

D is the only tested policy meeting both stress requirements, costing CNY 255 with 94% service and maximum time 5.7 hours. B fails the 90% service requirement at 84%; E passes service but fails the time bound. A single unconditional recommendation of B would therefore be invalid.

## Conclusion and limits
Use B on the specified base batch and D on the specified stress batch. Hard-constraint screening precedes cost comparison; low cost cannot compensate a violation. The analysis covers the complete five-policy comparison but not all possible dispatch rules. The given synthetic records and the table-screening calculation establish neither controller implementation fidelity nor physical or probabilistic reliability.
