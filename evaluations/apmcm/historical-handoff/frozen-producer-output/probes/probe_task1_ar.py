"""
Task 1 route probe: AR(p) least-squares parameter estimation as QUBO.

Question decided by this probe:
  Can fixed-point binary encoding of (c, phi_1..phi_p) + a quadratic
  SSE objective be solved by bit-flip SA to recover the classical OLS
  AR fit, and does the October forecast stabilize across bit widths
  and AR orders p in {1,2,3}?
Outputs are route-decision evidence only, not contest results.
"""
import json
import numpy as np
from pathlib import Path
from qubo_sa import sa_minimize, exact_minimize, energy_ols_bits

Y = np.array([9000, 9400, 9594, 9859, 9958, 10043, 10309, 10512, 10588],
             dtype=float)
S = 1000.0  # scale factor, explicit in the paper; z = y / 1000
z = Y / S

rng = np.random.default_rng(42)


def design(p):
    X, t = [], []
    for i in range(p, len(z)):
        X.append(np.r_[1.0, z[i - p:i][::-1]])  # [1, z_{t-1}, ..., z_{t-p}]
        t.append(z[i])
    return np.array(X), np.array(t)


def ols(X, t):
    th, res, *_ = np.linalg.lstsq(X, t, rcond=None)
    sse = float(np.sum((X @ th - t) ** 2))
    return th, sse


def bic(sse, n, k):
    return n * np.log(sse / n) + k * np.log(n)


results = {"scale": S, "orders": {}, "baselines": {}}

# Simple baselines for the October forecast (in original units)
results["baselines"]["naive_last"] = float(Y[-1])
tt = np.arange(9)
a0, a1 = np.polyfit(tt, Y, 1)
results["baselines"]["linear_trend_oct"] = float(a0 * 9 + a1)
results["baselines"]["mean_growth_oct"] = float(Y[-1] + np.mean(np.diff(Y)))

for p in (1, 2, 3):
    X, t = design(p)
    ntr = len(t)
    th_ols, sse_ols = ols(X, t)
    entry = {
        "n_train": ntr,
        "k_params": p + 1,
        "ols_theta_scaled": dict(zip(["c"] + [f"phi{i}" for i in range(1, p + 1)],
                                     np.round(th_ols, 6).tolist())),
        "ols_sse_scaled": round(sse_ols, 8),
        "ols_bic": round(bic(sse_ols, ntr, p + 1), 4),
        "oct_ols": None,
        "qubo": [],
    }
    # OLS October forecast (scaled units back to original)
    z10 = th_ols[0] + np.sum(th_ols[1:] * z[len(z) - p:][::-1])
    # z_{t-i}: for t=10 (index 9), phi_i multiplies z_{10-i} = z[9-i]
    z10 = th_ols[0] + sum(th_ols[i] * z[9 - i] for i in range(1, p + 1))
    entry["oct_ols"] = round(float(z10 * S), 3)

    # parameter ranges: c in [-2,2] (scaled), phi in [-2,2]
    ranges = [(-2.0, 2.0)] * (p + 1)
    for B in (6, 8, 10, 12):
        Q, decode, const = energy_ols_bits(X, t, ranges, B)
        nbits = Q.shape[0]
        best_x, best_e, run_es, acc = sa_minimize(
            Q, sweeps=1500, runs=10, seed=42)
        th_q = decode(best_x)
        sse_q = float(np.sum((X @ th_q - t) ** 2))
        z10q = th_q[0] + sum(th_q[i] * z[9 - i] for i in range(1, p + 1))
        rec = {
            "bits_per_param": B,
            "total_bits": nbits,
            "theta_sa": np.round(th_q, 6).tolist(),
            "sse_actual_sa": round(sse_q, 8),
            "sse_rel_vs_ols_sa": round((sse_q - sse_ols) / sse_ols, 6),
            "oct_forecast_sa": round(float(z10q * S), 3),
            "sa_energy": round(best_e + const, 8),
            "run_energy_spread": round(max(run_es) - min(run_es), 8),
        }
        if nbits <= 24:  # exact ground truth of the QUBO (formulation check)
            xe, ee = exact_minimize(Q)
            th_e = decode(xe)
            sse_e = float(np.sum((X @ th_e - t) ** 2))
            z10e = th_e[0] + sum(th_e[i] * z[9 - i] for i in range(1, p + 1))
            rec.update({
                "theta_exact": np.round(th_e, 6).tolist(),
                "sse_actual_exact": round(sse_e, 8),
                "sse_rel_vs_ols_exact": round((sse_e - sse_ols) / sse_ols, 6),
                "oct_forecast_exact": round(float(z10e * S), 3),
                "sa_hits_exact": bool(abs(best_e - ee) < 1e-9),
            })
        entry["qubo"].append(rec)
    results["orders"][p] = entry

out = Path(__file__).parent / "results" / "task1_probe.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, indent=2, ensure_ascii=False))

print("=== Task 1 AR-QUBO probe ===")
for p, e in results["orders"].items():
    print(f"p={p} n={e['n_train']} OLS theta={e['ols_theta_scaled']} "
          f"SSE={e['ols_sse_scaled']:.6f} BIC={e['ols_bic']} "
          f"Oct(OLS)={e['oct_ols']}")
    for q in e["qubo"]:
        line = (f"  B={q['bits_per_param']:2d} bits={q['total_bits']:3d} "
                f"SSErel(SA)={q['sse_rel_vs_ols_sa']:+.5f} "
                f"Oct(SA)={q['oct_forecast_sa']} "
                f"spread={q['run_energy_spread']:.2e}")
        if "sse_rel_vs_ols_exact" in q:
            line += (f" | exact SSErel={q['sse_rel_vs_ols_exact']:+.5f} "
                     f"Oct(exact)={q['oct_forecast_exact']} "
                     f"SA==exact:{q['sa_hits_exact']}")
        print(line)
print("baselines:", results["baselines"])
