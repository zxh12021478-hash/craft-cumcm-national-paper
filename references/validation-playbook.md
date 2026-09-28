# Validation and uncertainty playbook

## Select evidence from the claim's failure path

Start with the exact claim, the most plausible way it could be wrong, and the consequence of that
failure. Choose the lightest independent check that can expose that failure. Do not apply one
generic checklist to every model, and do not count a sensitivity plot as proof that the underlying
formulation, data split, parameter identification, or solver result is valid.

- prediction and classification: use deployment-aligned splits, leakage checks, calibration, and
  decision-relevant errors;
- ranking and evaluation: test weight and normalization uncertainty, rank reversal, dominance, and
  whether the recommended choice changes;
- deterministic optimization: verify feasibility from primitive variables, bounds or gaps, exact
  reduced instances, and realized or scenario regret; residual normality and p-values are usually
  irrelevant unless a statistical submodel supplies the inputs;
- mechanism and simulation: test dimensions, conservation or accounting identities, boundary and
  special cases, identifiability, and numerical convergence;
- sequential or spatial decisions: test temporal or network leakage, state-transition consistency,
  policy stability, and out-of-sample or perturbed-topology behavior.

Set acceptance thresholds from the task, data quality, physical or operational tolerance, or a
controlled baseline. Never invent a universal `pass` threshold or conclude robustness from one
arbitrary `±10%` perturbation.

## Analytical checks

- dimensional consistency and units;
- sign, domain, and range checks;
- boundary and degenerate cases;
- invariants and conservation;
- exact or known special cases;
- existence, uniqueness, monotonicity, or convexity where available;
- lower and upper bounds.

## Numerical checks

- grid/time-step/discretization convergence;
- multiple initializations and random seeds;
- objective convergence and constraint residuals;
- gradient or finite-difference checks;
- exact enumeration on reduced instances;
- alternative implementation of a critical calculation;
- runtime and memory behavior.

## Statistical checks

- split by time, entity, site, or group to match deployment;
- nested validation when tuning;
- residual independence, heteroscedasticity, distribution, and autocorrelation;
- calibration and interval coverage;
- class-wise precision, recall, specificity, and decision cost;
- uncertainty intervals for parameters and predictions;
- bootstrap or posterior checks;
- baseline and ablation comparisons.

## Optimization checks

- feasibility of every returned decision;
- lower/upper bound or relaxation gap;
- regret under realized/scenario data;
- robustness to input distributions and structural assumptions;
- Pareto frontier for conflicting objectives;
- policy-switch thresholds;
- comparison with a transparent policy.

## Controlled model comparison

Compare the baseline and proposed method under the same sample, split, scenario set, metric definitions, stopping rules, and resource assumptions whenever possible. Report predictive or objective improvement together with feasibility, runtime, uncertainty, and downstream decision impact. Use ablation to isolate the claimed modification.

## Independent recomputation

Name the main implementation's plausible failure path for every headline result. Recompute the
quantity from primitive saved variables with a separate formula, script, enumerator, bound, or
analytical identity. Do not count a copied function, cached residual, solver success flag, or two
algorithms sharing the same flawed formulation as independent evidence. Use
`scripts/truth_harness.py` for generic recomputation checks and add problem-specific checks where its
types are insufficient.

## Reality checks

For each headline output, record a plausible range or accounting/physical/operational identity, its source or derivation, the computed value, and the consequence of failure. A visually plausible chart is not a reality check.

## Evidence strength

Rank evidence: external or held-out reality > controlled synthetic recovery > analytical special case > independent implementation > solver agreement > internal fit. Use stronger evidence for stronger claims.

## Validation report template

For each claim record: claim, validation method, data used, metric, acceptance threshold, result, pass/fail, consequence, and repair.
