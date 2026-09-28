# Forecasting and downstream optimization kit

## Applicability and baseline

Use when future values are requested or predictions feed a later decision. Start with naive,
seasonal-naive, or simple regression baselines. Define forecast origin, horizon, information
available at prediction time, and downstream loss before fitting.

## Construction contract

- Split chronologically or by deployment unit; fit preprocessing only on training data.
- Report horizon-specific errors, residual diagnostics, calibration, and interval coverage.
- Audit target, feature, temporal, entity, and preprocessing leakage.
- Propagate predictive uncertainty into decisions with held-out scenarios, intervals, robust bounds,
  or approved chance constraints; compare predictive accuracy with decision loss.

## Independent verifier

Recreate split boundaries, naive forecasts, metrics, interval coverage, and downstream objective from
saved primitive predictions and decisions. Use evaluation scenarios not used by the optimizer and
verify that timestamps and entity IDs do not cross the declared boundary.

## Outputs and failure boundary

Deliver backtests, residual and coverage evidence, baseline comparison, decision frontier, and an
uncertainty-cost or value-of-information calculation. Reject a lower-error model when it worsens
feasibility, regret, or the actual decision objective.
