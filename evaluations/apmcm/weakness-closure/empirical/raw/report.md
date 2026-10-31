# Calibration report — observed pressure-volume data (10 rows)

## What the observed data support

- Two forms were fitted by least squares in the original response (no log transform): the affine baseline y = a + b x and the saturating form y = A(1 − e^(−k x)).
- Affine: a = 2.0799, b = 0.11257, calibration RSS = 2.2674. Its residuals show a systematic curved pattern (negative at both ends, positive in the middle), so a straight line misses the bending mechanism.
- Saturating: A = 220.834, k = 6.005×10⁻⁴, RSS = 0.00647, about 350 times smaller; residuals are small and show no monotone curvature (largest magnitude 0.065 at the ninth point).
- The nonlinear profile search converged at an interior point of [10⁻⁷, 0.1] with no boundary hit; an 81-point log coarse scan followed by seven bounded refinement rounds reached a final log-window width 2.7×10⁻¹⁰.
- Four predictions at the higher, previously unseen pressures are frozen from calibration only (536.8 → 60.85; 593.1 → 66.17; 689.1 → 74.83; 760.0 → 80.92 in source units). The affine model predicts higher values at every extrapolation point because it cannot bend toward the asymptote.

## Identification and uncertainty limits

- Ten points identify the parameters only conditional on the chosen functional forms; they do not establish that an exponential saturating law is the true mechanism versus other saturating curves.
- The profiled k is a point estimate; no standard error, profile-likelihood interval or residual-based uncertainty band is computed. Near-singular behavior for very small k was handled by the bounded profile, but parameter correlation between A and k is not quantified.
- Calibration fit quality is in-sample evidence. It cannot substitute for the four withheld responses, which were not read, and no holdout accuracy or headline gain is claimed.
- Source units and measurement precision are not stated; source units are preserved and no SI units or precision digits are invented.
- Parameters and predictions are frozen; no refit is permitted after later evaluation.

## Stronger validation that would actually matter

1. Evaluate the four frozen predictions against the withheld responses without refitting (absolute errors, holdout RSS, and whether the affine–saturating ranking persists out of the calibration range).
2. A profile interval for k and a residual-vs-pressure check to confirm the remaining ninth-point residual is not a systematic local failure.
3. If the writing agent later claims a physical adsorption interpretation, evidence beyond these ten points (the source dataset's experimental context and uncertainty) would be required; the current fit alone supports only a descriptive saturating relationship.
