# Problem-specific innovation patterns

## 1. Structural reduction

Prove that only a boundary, local neighborhood, critical time, active constraint, or representative state needs evaluation. Report the reduction in dimension or complexity and verify the proposition numerically.

## 2. Regime-switching model

Derive a criterion that selects between simple and complex mechanisms. Examples include low/high noise, sparse/dense demand, coherent/incoherent interference, uncongested/congested flow, or data-rich/data-poor regimes.

## 3. Identifiability-aware fusion

Use multiple angles, sensors, time points, groups, or experiments to break parameter confounding. Demonstrate identifiability with profile likelihood, Fisher information, posterior correlation, rank, or synthetic recovery.

## 4. Uncertainty-to-decision closure

Propagate observation and parameter uncertainty into predictive distributions and then into robust, stochastic, Bayesian, or chance-constrained decisions. Compare the decision with a plug-in point estimate.

## 5. Strategy boundary or phase diagram

Map where the optimal decision changes over key dimensionless parameters, cost ratios, noise levels, or resource limits. State stable regions and switching thresholds.

## 6. Value of information

Identify which additional measurement, sample, sensor, or experiment most reduces expected decision loss. Quantify expected value, not merely feature importance.

## 7. Structure-aware solver

Exploit separability, sparsity, geometry, monotonicity, dynamic programming, decomposition, warm starts, or event structure. Compare with a generic solver on quality, time, and feasibility.

## 8. Optimality or reliability certificate

Supply analytical bounds, relaxation gaps, interval enclosures, exact small-instance comparisons, calibration coverage, or verified constraint margins.

## 9. Decision-focused learning

Train or choose predictions by downstream decision regret rather than predictive error alone. Use only when the decision loss is well-defined and leakage is controlled.

## Anti-patterns

- renaming a standard algorithm;
- concatenating several models without a coherent mechanism;
- calling parameter tuning an innovation;
- dynamically changing heuristic parameters without a problem-specific rationale and controlled ablation;
- adding a hierarchy or weight correction without demonstrating that it repairs a named decision deficiency;
- adding deep learning to small tabular data without a baseline or calibration;
- calling correlation causal or substitutive;
- claiming robustness from one ±10% perturbation;
- using two similar heuristics as independent validation;
- inventing an acronym before demonstrating a substantive modification.

## Recommended final mix

Aim for one primary innovation and one or two supporting innovations:

- **Primary:** structural reduction, regime criterion, identifiability, or decision reformulation.
- **Supporting:** uncertainty closure, solver customization, validation certificate, or value of information.

Domain expertise counts only when it changes the mathematical object—such as constraints, priors, costs, risk measures, state dynamics, or validation ranges—and the consequence is tested.
