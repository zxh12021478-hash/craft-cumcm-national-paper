"""
Regression fix check for Task 1 (candidate-skill task-families):
information criteria across AR orders must use COMPARABLE response
samples and the same likelihood convention. The frozen probe computed
BIC with n=8/7/6 (different truncated prefixes), which is not a valid
order ranking. This deterministic, solver-free check recomputes OLS
and BIC on ONE common window t = pmax+1 .. 9 (6 observations) for all
p in {1,2,3}. It is not a QUBO/SA rerun; it is a closed-form
calculation on the nine values given in the original question.
"""
import json
from pathlib import Path
import numpy as np

Y = np.array([9000, 9400, 9594, 9859, 9958, 10043, 10309, 10512, 10588],
             dtype=float)
S = 1000.0
z = Y / S
PMAX = 3
common_idx = list(range(PMAX, len(z)))  # 0-based 3..8 -> t=4..9, n=6


def design(p, idxs):
    X, t = [], []
    for i in idxs:
        X.append([1.0] + [z[i - j] for j in range(1, p + 1)])
        t.append(z[i])
    return np.array(X), np.array(t)


out = {"common_response_indices_1based": [i + 1 for i in common_idx],
       "n_common": len(common_idx), "bic_formula": "n*ln(SSE/n)+k*ln(n)",
       "orders": {}}
for p in (1, 2, 3):
    X, t = design(p, common_idx)
    th, *_ = np.linalg.lstsq(X, t, rcond=None)
    sse = float(np.sum((X @ th - t) ** 2))
    k = p + 1
    n = len(common_idx)
    bic = n * np.log(sse / n) + k * np.log(n)
    aic = n * np.log(sse / n) + 2 * k
    out["orders"][p] = {
        "k": k, "sse_scaled": round(sse, 8),
        "bic_common_window": round(float(bic), 4),
        "aic_common_window": round(float(aic), 4),
        "theta_scaled_common_fit": np.round(th, 6).tolist()}

# Final per-order forecasts use the maximal sample fit for each p
# (frozen probe already produced these); recompute here for completeness.
final = {}
for p in (1, 2, 3):
    idxs = list(range(p, len(z)))
    X, t = design(p, idxs)
    th, *_ = np.linalg.lstsq(X, t, rcond=None)
    z10 = th[0] + sum(th[i] * z[9 - i] for i in range(1, p + 1))
    final[p] = {"theta_max_sample": np.round(th, 6).tolist(),
                "oct_forecast_ols": round(float(z10 * S), 3)}
out["max_sample_final_fits_ols"] = final
out["note"] = ("Selection is restricted to common-window BIC above; "
               "final fit per p uses all usable observations and is "
               "not an order-selection statistic.")

Path(__file__).parent.mkdir(exist_ok=True)
outp = Path(__file__).parent / "t1_common_window_bic.json"
outp.write_text(json.dumps(out, indent=2, ensure_ascii=False))
print("common window (1-based t):", out["common_response_indices_1based"])
for p, e in out["orders"].items():
    print(f"p={p} k={e['k']} SSE={e['sse_scaled']:.6f} "
          f"BIC={e['bic_common_window']} AIC={e['aic_common_window']}")
for p, e in final.items():
    print(f"max-sample OLS p={p} Oct={e['oct_forecast_ols']}")
