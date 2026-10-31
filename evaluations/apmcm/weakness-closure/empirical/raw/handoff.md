# Handoff — next executable validation for the writing agent

## Frozen state (do not refit)

- Inputs: 10 calibration rows from `../train.json`; code `fit.py`; machine output `results.json`.
- Frozen parameters: affine a = 2.079884, b = 0.112572; saturating A = 220.834497, k = 0.00060047.
- Frozen four-point predictions in source units:
  - 536.8 → affine 62.509 / saturating 60.849
  - 593.1 → 68.847 / 66.168
  - 689.1 → 79.653 / 74.831
  - 760.0 → 87.635 / 80.917

## Next meaningful executable check

1. Read the withheld four responses (held by root; not available in this receiver folder) and match them to the frozen predictions in pressure order.
2. Compute, without refitting either model: per-point absolute error, holdout RSS, and max error for the affine and saturating forms; record whether the saturating model stays lower in error outside the calibration range.
3. Apply the predeclared decision rule: if saturating holdout RSS is lower, retain it as the recommended descriptive model; if not, report the failure honestly and keep the affine baseline as the supported comparison — no parameter adjustment after seeing the labels.
4. Only after that, if a physical interpretation is to be written, add a profile-likelihood interval for k and a residual-pattern check; do not upgrade the calibration fit into validated adsorption mechanics without this evidence.

## Boundaries

- Same-conversation development work, not independent validation; no network, installs, paid services or Modex were used.
- Units stay as source units; no holdout accuracy is stated in this package because the labels were not supplied.
- Any claim beyond the frozen 10-point calibration must cite the new holdout evidence; it must not be inferred from the small in-sample RSS.
