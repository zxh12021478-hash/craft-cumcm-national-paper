# Forecast feature availability guard

Use when a forecast probe or returned code uses delayed or future exogenous variables. A historical CSV contains values known today; that does not mean they were known at each historical forecast origin. A one-period lag may still be unavailable if publication is delayed. Check the actual code, not just its prose description.

Trace derived features back to their ingredients as well as their release times. A contemporaneous ratio, per-capita value, share or residual computed from the target still contains that target: if `E_t = M_t / N_t`, supplying actual `E_t` to forecast unknown `M_t` is not an independent predictor. A new column name or high fitted R² does not remove the dependence. Use genuinely available lags or independently formed forecasts/scenarios for the ingredients; if solving a simultaneous structural system, state and identify that system instead of treating the constructed feature as observed input. The optional timestamp checker below cannot discover hidden construction dependencies or validate a falsely labeled scenario.

Optionally emit a small feature-use trace from the calculation and check it with:

```bash
python3 scripts/check_information.py --trace information.json --output information-audit.json
```

All time indices use one numeric unit (e.g. week). `availability_lags` gives release time minus source time. This example must fail: promotion for week 83 releases at week 81, after origin 80.

```json
{
  "availability_lags": {"promotion": -2, "tickets": 1},
  "forecasts": [{"id": "o80-h3", "origin": 80, "target": 83,
    "features": [{"name": "promotion", "source_time": 83, "kind": "observed"}]}]
}
```

For an explicitly assumed scenario or a genuinely generated forecast, use `kind: "scenario"` or `"forecast"`, with `formed_at` and a `note` describing its assumption/method. Do not relabel an actual future observation as a scenario to pass the guard. Preserve the scenario and observation distinction in backtests and conclusions; the script does not establish scenario probabilities or inspect whether the trace matches the code.

Record actual origin/horizon, sample count and metric aggregation. A pooled h=1…4 error is not an h=4-only error. If a probe fails availability, exclude its accuracy figures from the handoff, repair and rerun the relevant comparison, and preserve the failed version.
