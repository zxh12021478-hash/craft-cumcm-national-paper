# Optimization and scheduling kit

## Applicability and baseline

Use when decisions allocate, route, schedule, pack, locate, or select under constraints. State every
decision variable, objective unit, hard constraint, information assumption, and feasible-set meaning
before choosing a solver. Use an auditable heuristic or relaxation as baseline.

## Construction contract

- Separate hard constraints from penalties and team preferences.
- Predeclare feasibility tolerances, stopping rules, budgets, and comparison resources.
- Report lower/upper bounds or optimality gaps when available; never infer global optimality from a success flag.
- Test multiple starts or solvers, active constraints, parameter stress, scenario regret, and trade-offs.

## Independent verifier

Load primitive decision variables and independently recompute the complete objective and every
constraint residual. On reduced instances, enumerate or solve exactly; compare bounds and detect
indexing, sign, unit, integrality, and omitted-constraint errors.

## Outputs and failure boundary

Deliver the solution, objective decomposition, constraint-slack table, bounds/gaps, runtime evidence,
scenario regret, and Pareto frontier. Any material hard-constraint violation is an automatic failure,
regardless of objective quality or solver status.
