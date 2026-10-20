# Minimum-cost modular supply for a specified contingency set

## Task
Q1. Choose a subset of three available modules, at most one of each, with minimum installation cost. Under normal operation total supply must be at least 7 units/day. Under loss of any one installed module, remaining supply must be at least 3 units/day. Modules are indivisible; capacities add without losses. Q2. For the selected design, give remaining supply under each of its single-module failures. These are the entire finite set of stipulated conditions, not random samples or forecasts.

## Summary
We enumerate all eight subsets of three supply modules to minimize installation cost under normal and single-module-failure requirements. Installing A and B costs CNY 12 and supplies 7 units/day normally. If A fails, B retains 3 units/day; if B fails, A retains 4, both meeting the required 3. The design is the unique minimum among the complete finite candidate set and costs 20% less than the specified capacity-first reference B+C at CNY 15. This exact result applies to the stated additive-capacity model and contingency set, without claiming measured hardware reliability or performance under unspecified multiple failures.

## Model and baseline
Installed binary variables x_A,x_B,x_C select capacities 4,3,5 units/day and installation costs 7,5,10 CNY. Minimize 7x_A+5x_B+10x_C, subject to normal supply at least 7, and for each installed module j subtract its capacity and require at least 3 units/day remaining. The reference installs the largest-capacity module C first, then B to meet the normal and contingency constraints; B+C costs 15 and supplies 8 normally, 3 or 5 after one failure. The reference is a specified comparison, not a claim that it is the strongest possible heuristic. No randomized search, learned parameters, module-effect attribution, probability law or external samples are involved.

## Exact solution and proof
The provided solve.py enumerates the full 2^3=8 candidate set and directly recomputes all stipulated constraints and costs with integer arithmetic. Exactly four designs are feasible: A+B cost 12, B+C cost 15, A+C cost 17, A+B+C cost 22. All remaining subsets fail normal supply. The unique lowest feasible cost is 12, attained by A+B. Its normal supply is 7. Removing A leaves 3; removing B leaves 4, so the worst specified post-failure supply is 3. The reduction relative to the capacity-first reference is (15-12)/15=20%. This is a complete finite-enumeration certificate for the supplied model, not merely solver status. The generated results.json records all eight rows, not just successes.

## Conclusion and limits
Choose A+B for Q1 and retain 3 or 4 units/day under the two specified failures for Q2. The exact optimum needs no held-out data: all model inputs and the finite contingency set are given by the task. No hardware measurements, unmodeled failure probabilities, physical capacity validation or generalization to unknown contingencies are established. These limits do not invalidate the exact solution to this specified mathematical problem.
