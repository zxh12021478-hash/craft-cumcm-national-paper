#!/usr/bin/env python3
"""fit.py — observed-data calibration receiver (stdlib math only).

Fits the first 10 pressure-volume rows:
  affine baseline     y = a + b x
  saturating model    y = A (1 - exp(-k x)), profiled over k with
                      A = sum(f*y)/sum(f*f) for fixed k.
Least squares in original y (no log transform). The four higher-pressure
responses are not read; predictions are frozen from calibration only.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, "..", "train.json")
OUT_JSON = os.path.join(HERE, "results.json")

train = json.load(open(TRAIN))
rows = train["calibration_rows"]
x = [r["pressure"] for r in rows]
y = [r["volume"] for r in rows]
new_pressures = train["prediction_pressures"]
n = len(x)


def rss(actual, predicted):
    return sum((a - p) ** 2 for a, p in zip(actual, predicted))


# ---------------------------------------------------------------------------
# affine baseline: closed-form OLS
# ---------------------------------------------------------------------------
mx = sum(x) / n
my = sum(y) / n
b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / \
    sum((xi - mx) ** 2 for xi in x)
a = my - b * mx
affine_pred = [a + b * xi for xi in x]
affine = {"a": a, "b": b,
          "residuals": [yi - (a + xi * b) for xi, yi in zip(x, y)],
          "RSS": rss(y, affine_pred)}


# ---------------------------------------------------------------------------
# saturating model: profile over k
# ---------------------------------------------------------------------------
def fixed_k(k):
    f = [1 - math.exp(-k * xi) for xi in x]
    sff = sum(v * v for v in f)
    A = sum(fi * yi for fi, yi in zip(f, y)) / sff
    pred = [A * fi for fi in f]
    return A, pred, rss(y, pred)


K_LO, K_HI = 1e-7, 0.1
# broad log coarse scan, 81 points
coarse_n = 81
log_lo, log_hi = math.log(K_LO), math.log(K_HI)
coarse_grid = [math.exp(log_lo + (log_hi - log_lo) * i / (coarse_n - 1))
               for i in range(coarse_n)]
coarse_eval = []
best = None
for k in coarse_grid:
    A, _, rss_k = fixed_k(k)
    coarse_eval.append((k, rss_k))
    if best is None or rss_k < best[1]:
        best = (k, rss_k, A)

# bounded log refinement: shrink a log window around the current best
refine_log = []
lo_idx = coarse_grid.index(best[0]) - 1
hi_idx = coarse_grid.index(best[0]) + 1
win_lo = coarse_grid[max(0, lo_idx)]
win_hi = coarse_grid[min(coarse_n - 1, hi_idx)]
rounds = 0
for rounds in range(1, 9):
    grid = [math.exp(math.log(win_lo) + (math.log(win_hi) - math.log(win_lo))
                     * i / 40) for i in range(41)]
    round_best = None
    for k in grid:
        A, _, rss_k = fixed_k(k)
        if round_best is None or rss_k < round_best[1]:
            round_best = (k, rss_k, A)
    rel_width = (math.log(win_hi) - math.log(win_lo))
    refine_log.append({"round": rounds, "window": [win_lo, win_lo],
                        "log_width": rel_width,
                        "best_k": round_best[0], "best_RSS": round_best[1]})
    best = round_best
    i_best = grid.index(best[0])
    if i_best == 0 or i_best == 40:
        # expand rather than silently stop at a refinement-window edge
        win_lo = grid[max(0, i_best - 1)]
        win_hi = grid[min(40, i_best + 1)]
    else:
        win_lo = grid[i_best - 1]
        win_hi = grid[i_best + 1]
    if rel_width < 1e-8:
        break

k_hat, rss_sat, A_hat = best
A_hat, sat_pred, rss_sat = fixed_k(k_hat)
saturating = {
    "A": A_hat, "k": k_hat,
    "residuals": [yi - pi for yi, pi in zip(y, sat_pred)],
    "RSS": rss_sat,
    "optimization": {
        "method": "profile LS over k; A = sum(f*y)/sum(f*f), f=1-exp(-k x)",
        "search_range": [K_LO, K_HI],
        "coarse_grid_points": coarse_n,
        "refinement_rounds": rounds,
        "final_log_window_width": math.log(win_hi) - math.log(win_lo),
        "lower_boundary_hit": abs(k_hat - K_LO) / K_LO < 1e-6,
        "upper_boundary_hit": abs(k_hat - K_HI) / K_HI < 1e-6,
        "interior_solution": K_LO < k_hat < K_HI,
        "log_window_stopping_met": math.log(win_hi)-math.log(win_lo) < 1e-8},
}

# ---------------------------------------------------------------------------
# frozen predictions at the four higher pressures (no withheld labels used)
# ---------------------------------------------------------------------------
predictions = []
for p in new_pressures:
    predictions.append({
        "pressure": p,
        "affine_volume": a + b * p,
        "saturating_volume": A_hat * (1 - math.exp(-k_hat * p))})

results = {
    "data_scope": {"n_calibration": n,
                   "source_units": "source units; units not stated, none invented",
                   "fit_domain": "first 10 increasing-pressure rows only",
                   "objective": "least squares in original y; no log transform"},
    "affine": affine,
    "saturating": saturating,
    "rss_comparison": {"affine": affine["RSS"], "saturating": rss_sat,
                       "saturating_lower_RSS": rss_sat < affine["RSS"]},
    "frozen_predictions": predictions,
    "limitations": [
        "four higher-pressure responses were not read; no holdout accuracy claimed",
        "profiled k is a calibration point estimate with no uncertainty interval",
        "point estimates are conditional on chosen forms; physical parameter identification not established",
        "predictions are frozen; no refit after later evaluation",
        "no measurement precision or units supplied; none invented"],
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2, sort_keys=True)
print("affine a=%.6f b=%.6f RSS=%.6f" % (a, b, affine["RSS"]))
print("saturating A=%.6f k=%.8f RSS=%.6f" % (A_hat, k_hat, rss_sat))
print("boundary hits:", saturating["optimization"]["lower_boundary_hit"],
      saturating["optimization"]["upper_boundary_hit"])
print("wrote results.json")
