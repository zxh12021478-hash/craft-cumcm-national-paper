# Physical validation for engineering models

Match validation to the claim. Numerical verification tests the implemented equations; empirical validation tests their relevance to observations. Neither a software pass nor a second AI opinion establishes real-world accuracy or an award level.

## Freeze before testing

Keep the submitted baseline immutable. Record model/input hashes, observables, domain, boundary conditions, calibration versus holdout split, comparison metrics and decision tolerances before inspecting test outcomes. Set tolerances from the intended decision and measurement uncertainty; label analyst-chosen screening thresholds as such. Keep a failed test failed after a repair and record a separate revised model/version.

## Check consequential mechanisms

- Trace energy, dry air, water and pollutant mass across equations and device boundaries. Account for fan/pump heat, latent loads and external heat rejection at the accuracy level needed by the claim.
- Check analytic limits, constant states, independent conservation and positivity. Vary time step and spatial resolution separately for the same continuous equations; a changed stencil or parameter meaning is a changed model, not convergence.
- Test shape, parameter and objective-weight changes through the actual recommendation. Report rank changes and regret. Frequencies over selected scenarios are not probabilities of physical truth.
- Compare appropriate observables with primary experimental or established benchmark data. Preserve raw measurements, units, provenance and conversion code. Explain geometry, operating-condition and scale mismatches. A model with no velocity state cannot be declared validated against measured velocity profiles.
- Separate fitting from assessment. Hold out independent conditions or locations where possible; expose measurement uncertainty, residual patterns and failure regions. Published product specifications are not observations of the proposed design.

## Report and repair

Use a validation ledger with test, status, metric, threshold/rationale, evidence, model version and effect on claims. Distinguish pass, fail, not-applicable and unverified. When a failed mechanism affects the answer, repair and rerun it, or narrow/withdraw the answer. Update the Modex handoff so rejected claims are not polished back into the paper. Empirical gaps that require new hardware measurements must be named specifically; do not manufacture an experiment or rename a synthetic benchmark as measured data.
