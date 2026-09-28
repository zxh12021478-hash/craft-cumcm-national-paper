# Classification, recognition, and warning kit

## Applicability and baseline

Use when the output is a class, anomaly, warning tier, or action threshold. Start with an
interpretable linear or shallow-tree baseline using a split that matches deployment.

## Construction contract

- Freeze the observation unit, label timing, leakage boundary, class costs, and decision threshold.
- Match validation to time, entity, site, or group deployment; use nested validation when tuning.
- Report per-class precision, recall, specificity, calibration, subgroup performance, and repeated-split uncertainty.
- Compare threshold choices by decision cost, not accuracy alone; ablate features with plausible leakage risk.

## Independent verifier

Recompute the confusion matrix, per-class metrics, calibration bins, warning tiers, and cost from
saved labels, probabilities, groups, and thresholds. Verify no entity or future information crosses
the split and test label permutation or a simple baseline to expose leakage.

## Outputs and failure boundary

Deliver error-cost and subgroup tables, calibration evidence, feature evidence, threshold curves,
and actionable tiers. Accuracy alone is invalid under imbalance or unequal costs; a warning system
fails if calibration or the operating threshold is not supported at deployment prevalence.
