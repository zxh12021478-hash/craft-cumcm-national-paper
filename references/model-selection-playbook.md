# Model-selection playbook

## First classify the task

| Task | Baseline families | Stronger directions | Common failure |
|---|---|---|---|
| Geometry/kinematics | coordinate geometry, ODE, recursion | invariants, collision localization, event-driven simulation | brute-force discretization without error control |
| Physical measurement/inverse problem | first-principles observation equation, least squares | identifiability, joint multi-channel fit, model-regime criterion | fitting a curve without a measurement mechanism |
| Dynamic system/control | ODE/PDE/state space | nondimensionalization, stability, optimal control, surrogate-assisted search | solver output with no stability or boundary analysis |
| Allocation/scheduling | LP/MILP, dynamic programming | decomposition, valid inequalities, robust/stochastic optimization | arbitrary heuristic where exact structure is available |
| Forecasting | naive/seasonal baseline, regression | hierarchical/time-aware model, calibration, conformal intervals | random train-test split on time or entities |
| Classification | logistic/tree baseline | class-specific mechanism, calibration, cost-sensitive decision | accuracy-only reporting or leakage |
| Ranking/evaluation | explicit utility model | preference robustness, partial order, uncertainty | AHP/entropy weights without decision justification |
| Network/spatial | graph metrics, spatial regression | flow, diffusion, topology-aware optimization | treating spatial observations as independent |

## Candidate comparison matrix

Score each candidate from 1–5 on:

- mechanism fidelity;
- assumption burden;
- identifiability;
- data sufficiency;
- computational feasibility within competition time;
- interpretability;
- independent validation options;
- uncertainty handling;
- novelty potential;
- decision usefulness.

Do not select by total score alone. A score of 1 in identifiability, compliance, or validation is disqualifying unless repaired.

## Structural questions before algorithms

- Can variables be eliminated analytically?
- Is the solution monotone in any parameter?
- Does symmetry create equivalent cases?
- Is there a conserved quantity or dimensional group?
- Can the objective be decomposed by time, entity, route, or scenario?
- Is only a boundary or critical event relevant?
- Are some observations sufficient statistics?
- Does the optimal policy switch at identifiable thresholds?
- Are multiple parameters confounded?
- Can a lower/upper bound certify heuristic quality?

## Model escalation rule

Start with a baseline. Add complexity only when diagnostics show a named deficiency and the added component yields measurable improvement under independent validation. Record the baseline, deficiency, modification, and gain.

## Final-paper parsimony

Explore broadly during strategy selection, but normally write around one primary model and one transparent baseline or informative comparator. Use additional models only when different subproblems require different mechanisms or when a comparator tests a specific claim. Do not count preprocessing, weighting, optimization, and plotting as four separate models.

The AI may score and recommend candidates. The team must approve the final route, assumptions, objectives, constraints, and tradeoffs before implementation is treated as authoritative.
