# Stage: sensitivity analysis

Read `references/validation-playbook.md`.

## Purpose

Test whether the conclusion survives plausible changes. Do not perturb every parameter by an arbitrary percentage and call the model robust.

## Procedure

1. Rank uncertain inputs by expected decision impact.
2. Assign justified ranges or distributions from measurement error, literature, sampling, or scenario definitions.
3. Use local derivatives only for smooth local behavior. Use global variance, Latin hypercube, Monte Carlo, profile analysis, or scenario grids for nonlinear interactions.
4. Track changes in final decisions, feasibility, ranking, and regret—not only objective value.
5. Locate thresholds where the recommended strategy changes and display a robustness frontier or phase diagram.
6. Distinguish parameter sensitivity, structural sensitivity, data sensitivity, solver sensitivity, and assumption sensitivity.

## Output

State stable conclusions, fragile conclusions, controlling parameters, switching thresholds, and recommended safety margins. Feed material findings back into the abstract, conclusion, limitations, and decision recommendation.

