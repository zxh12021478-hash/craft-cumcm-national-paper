# Physical validation for engineering models

Match validation to the claim. Numerical verification tests the implemented equations; empirical validation tests their relevance to observations. Neither a software pass nor a second AI opinion establishes real-world accuracy or an award level.

## Freeze before testing

Keep the submitted baseline immutable. Record model/input hashes, observables, domain, boundary conditions, calibration versus holdout split, comparison metrics and decision tolerances before inspecting test outcomes. Set tolerances from the intended decision and measurement uncertainty; label analyst-chosen screening thresholds as such. Keep a failed test failed after a repair and record a separate revised model/version.

Freeze what each split is allowed to decide, not just its row IDs. If a returned handoff says “choose whichever model wins the final holdout”, that holdout has become selection data; report it as such and use another assessment if an independent performance claim is needed. A proposed next step is not a predeclared rule merely because a receiver calls it one. Compare frozen candidates without refitting or selecting on the reserved evaluation when that is the agreed purpose.

Before a large sweep, run a small pilot at a stable time step and one additional resolution. Resolve a failed conservation, stability or model-definition check before increasing candidate count. Keep numerical failure separate from physical discrepancy; a divergent integrator is not evidence against the continuous equations.

## Check consequential mechanisms

- Trace energy, dry air, water and pollutant mass across equations and device boundaries. Account for fan/pump heat, latent loads and external heat rejection at the accuracy level needed by the claim.
- Check analytic limits, constant states, independent conservation and positivity. Vary time step and spatial resolution separately for the same continuous equations; a changed stencil or parameter meaning is a changed model, not convergence.
- Test shape, parameter and objective-weight changes through the actual recommendation. Report rank changes and regret. Frequencies over selected scenarios are not probabilities of physical truth.
- Compare appropriate observables with primary experimental or established benchmark data. Preserve raw measurements, units, provenance and conversion code. Explain geometry, operating-condition and scale mismatches. A model with no velocity state cannot be declared validated against measured velocity profiles.
- Separate fitting from assessment. Hold out independent conditions or locations where possible; expose measurement uncertainty, residual patterns and failure regions. Published product specifications are not observations of the proposed design.

Match identification to the claimed output: a well-fitted response curve can still leave an asymptote or extrapolated physical parameter unstable. Inspect parameter tradeoffs and signed held-out errors when those parameters drive the recommendation; small training residuals or a better holdout point error alone do not establish calibrated uncertainty or a true mechanism. A parameter lying inside its search bounds is not a convergence test; retain the actual stopping/stationarity or independent fit check separately.

## Report and repair

For a time/amplitude transform, recompute derivatives and integrate over the transformed duration. If `theta_s(t)=a*theta(t/s)` on `[0,s*T]`, velocity scales as `a/s` and acceleration as `a/s^2`; the time measure changes too. Fixed task timing or endpoint requirements may rule out this transform before optimization. With always-on base power and nonnegative additional electrical draw, `E >= sum(P_base)*duration`; this bound needs the stated activation schedule and draw convention. Signed `torque*speed` is mechanical power: its closed-cycle integral can cancel acceleration against braking and is not battery consumption without a drive/loss/regeneration model. Define that convention rather than applying an unconditional absolute value. Base energy grows with duration, so slowing is not a universal energy-saving mechanism. A short analytic bound or one transformed-trajectory integration can reject a route before a solver sweep; it does not validate the robot hardware.

For spatial or temporal fields, align coordinates, times, units and observables before comparison. Use matched-point errors or appropriate profiles with residual maps and failure regions; equal extrema or overlapping value ranges can hide a reversed field. A commercial simulator is a numerical comparator with its own assumptions, not measured truth. Shared model error can survive agreement between two solvers. Scale the comparison to the decision and available budget rather than requiring full CFD for every problem.

Apply each constraint to its actual variable, spatial region and time scope. For example, a supply-air control temperature outside a crop comfort band does not by itself prove the crop-zone field violates that band. Trace the constrained observable before declaring infeasibility; do not repair a model by imposing a bound on the wrong quantity.

Use a validation ledger with test, status, metric, threshold/rationale, evidence, model version and effect on claims. Distinguish pass, fail, not-applicable and unverified. When a failed mechanism affects the answer, repair and rerun it, or narrow/withdraw the answer. Update the Modex handoff so rejected claims are not polished back into the paper. Empirical gaps that require new hardware measurements must be named specifically; do not manufacture an experiment or rename a synthetic benchmark as measured data.
