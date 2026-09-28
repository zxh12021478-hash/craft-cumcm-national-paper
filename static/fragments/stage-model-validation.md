# Stage: model validation

Read `references/validation-playbook.md` and `references/code-quality.md`.

## Validation stack

Use at least three independent layers when applicable:

1. **Analytical:** units, boundary cases, invariants, known special cases, proofs, or bounds.
2. **Numerical:** convergence, residuals, constraint violations, multiple seeds, solver comparison, precision study.
3. **Empirical:** held-out, rolling-origin, grouped cross-validation, external data, or benchmark comparison.
4. **Decision:** regret, feasibility under perturbation, stress scenarios, and policy stability.

## Independence rule

Validation must not simply repeat the same assumptions and implementation. Two metaheuristics agreeing is weak evidence if both optimize the same flawed formulation.
For every headline quantity, name the main failure path and choose a verifier that avoids it. Prefer recomputation from primitive saved variables, an analytical identity, reduced-instance enumeration, or a separately implemented metric over reading a solver success flag or cached residual.

## Required checks

- verify every reported headline number from code;
- calculate and report constraint violations;
- compare against a naive baseline;
- test at least one failure case;
- inspect residual structure and calibration, not only aggregate accuracy;
- report uncertainty with the final result;
- distinguish validation data from data used for fitting or tuning.
- compare results with domain ranges, conservation or accounting identities, operational feasibility, and simple back-of-the-envelope calculations;
- predeclare acceptance thresholds for headline comparisons when practical.

If validation fails, revise the model or narrow the claim. Never hide the failure.
