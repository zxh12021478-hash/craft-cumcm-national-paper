#!/usr/bin/env python3
"""Independent verification for the synthetic returned-draft audit.

Reads ONLY the audit-input files. Never modifies them.
Checks:
  Q1: recompute every percentage claimed in paper.md from results.json.
  Q2: (a) execute the supplied dispatch.py battery update;
      (b) check the claimed plan under two efficiency conventions;
      (c) analytic feasibility bounds;
      (d) independent LP feasibility test (scipy);
      (e) minimal uniform grid-cap relaxation via binary search (audit context).
  Q3/Q4/Q5: structural checks against results.json keys and paper text.
Outputs: stdout report (redirected to verify_output.txt) and verify_results.json.
"""
import importlib.util
import json
import pathlib
import sys

import numpy as np
from scipy.optimize import linprog

INPUT = pathlib.Path(__file__).resolve().parent.parent / "audit-input"
OUT = pathlib.Path(__file__).resolve().parent

report = []
def log(msg=""):
    print(msg)
    report.append(str(msg))

results = {}

# ---------------------------------------------------------------- Q1 numbers
rj = json.loads((INPUT / "results.json").read_text())
paper = (INPUT / "paper.md").read_text()

proxy = rj["comfort_proxy"]
energy = rj["electrical_energy_kWh"]
cost = rj["cost_CNY"]

proxy_drop = (proxy["baseline"] - proxy["design"]) / proxy["baseline"]
energy_drop = (energy["baseline"] - energy["design"]) / energy["baseline"]
cost_drop = (cost["baseline"] - cost["design"]) / cost["baseline"]

log("=== Q1 recomputed changes from results.json ===")
log(f"comfort proxy  {proxy['baseline']} -> {proxy['design']}: drop = {proxy_drop:.2%}")
log(f"electrical kWh {energy['baseline']} -> {energy['design']}: drop = {energy_drop:.2%}")
log(f"cost CNY       {cost['baseline']} -> {cost['design']}: drop = {cost_drop:.2%}")
log("paper summary claims electricity consumption -20%  -> matches energy? "
    f"{abs(energy_drop - 0.20) < 1e-9}; matches proxy? {abs(proxy_drop - 0.20) < 1e-9}")
log("paper Q1 claims cost -25% -> recomputed 20%: "
    f"{'CONTRADICTION' if abs(cost_drop - 0.25) > 1e-9 else 'ok'}")
results["q1"] = {
    "proxy_drop": proxy_drop, "energy_drop": energy_drop, "cost_drop": cost_drop,
    "summary_20pct_matches_energy": bool(abs(energy_drop - 0.20) < 1e-9),
    "summary_20pct_matches_proxy": bool(abs(proxy_drop - 0.20) < 1e-9),
    "cost_25pct_claim": abs(cost_drop - 0.25) > 1e-9,
}

# ---------------------------------------------------------------- Q2 dispatch
spec = importlib.util.spec_from_file_location("dispatch_supplied", INPUT / "dispatch.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

grid = rj["dispatch"]["grid"]
charge = rj["dispatch"]["charge"]
discharge = rj["dispatch"]["discharge"]
load = [4, 7, 5]
ETA = 0.9

log("\n=== Q2 claimed plan ===")
log(f"load={load}, grid={grid}, charge={charge}, discharge={discharge}")
states_supplied = mod.battery_energy(charge, discharge)
log(f"supplied dispatch.py states (E_t = E_{{t-1}} + 0.9 c - 0.9 d): {states_supplied}")
log(f"any negative stored energy: {any(e < -1e-12 for e in states_supplied)}")
log(f"final stored energy == 0: {abs(states_supplied[-1]) < 1e-12} "
    f"(actual {states_supplied[-1]})")

# Convention A: literal draft update; discharge delivers 0.9*d to the load.
log("\n-- Convention A (draft literal): E += 0.9c - 0.9d; load balance g + 0.9d - c = L --")
E = 0.0
for t in range(3):
    E = E + ETA * charge[t] - ETA * discharge[t]
    serve = grid[t] + ETA * discharge[t] - charge[t]
    log(f"h{t+1}: E={E:+.3f}, served={serve:.2f}, load={load[t]}, "
        f"balance_ok={abs(serve-load[t]) < 1e-9}, E>=0={E >= -1e-12}")

# Convention B: standard two-efficiency model; d is energy delivered to load,
# storage decrement d/0.9; load balance g + d - c = L.
log("\n-- Convention B (standard): E += 0.9c - d/0.9; balance g + d - c = L --")
E = 0.0
for t in range(3):
    E = E + ETA * charge[t] - discharge[t] / ETA
    serve = grid[t] + discharge[t] - charge[t]
    log(f"h{t+1}: E={E:+.3f}, served={serve:.2f}, load={load[t]}, "
        f"balance_ok={abs(serve-load[t]) < 1e-9}, E>=0={E >= -1e-12}")
log(f"final E == 0 under B: {abs(E) < 1e-12} (actual {E:.3f})")

# Analytic bounds
log("\n=== Analytic feasibility bounds (solar = 0, E0 = E3 = 0) ===")
total_load = sum(load)
max_grid = 3 * 5
log(f"total load = {total_load}; max grid over 3 h = {max_grid}; "
    f"battery round-trip eta^2 = {ETA**2:.2f} < 1")
log("Convention B aggregate: sum(g) = 16 + (1-eta^2) sum(c) >= 16 > 15  -> infeasible")
log("Convention A aggregate: sum(g) = 16 + 0.1 sum(c) >= 16 > 15  -> infeasible")
# hour-2 bound, convention B
c1_max = 5 - load[0]                      # g1 <= 5 and g1 = 4 + c1
E1_max = ETA * c1_max
d2_delivered_max = ETA * E1_max           # 0.9 * stored
log(f"h1: c1 <= {c1_max} (grid cap after serving load 4) -> E1 <= {E1_max:.2f}")
log(f"h2: max delivered from storage = 0.9*E1 = {d2_delivered_max:.2f}; "
    f"max served = 5 + {d2_delivered_max:.2f} = {5 + d2_delivered_max:.2f} < 7")

# Independent LP feasibility tests.
# Variables: [g1,g2,g3, c1,c2,c3, d1,d2,d3, E1,E2,E3]
def lp_feasible(gcap, convention):
    A_eq, b_eq = [], []
    for t in range(3):
        row = np.zeros(12)
        row[t] = 1.0          # g
        row[3 + t] = -1.0     # c
        if convention == "A":
            row[6 + t] = ETA     # 0.9 d delivered
        else:
            row[6 + t] = 1.0     # d delivered
        A_eq.append(row); b_eq.append(load[t])
    # E_t - E_{t-1} - 0.9 c_t (+ d/0.9 for B) = 0, E0 = 0
    for t in range(3):
        row = np.zeros(12)
        row[9 + t] = 1.0
        if t > 0:
            row[9 + t - 1] = -1.0
        row[3 + t] = -ETA
        if convention == "A":
            row[6 + t] = ETA
        else:
            row[6 + t] = 1.0 / ETA
        A_eq.append(row); b_eq.append(0.0)
    # E3 = 0
    row = np.zeros(12); row[11] = 1.0
    A_eq.append(row); b_eq.append(0.0)
    bounds = [(0, gcap)] * 3 + [(0, 2)] * 3 + [(0, 2)] * 3 + [(0, None)] * 3
    res = linprog(np.zeros(12), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=bounds, method="highs")
    return res

for conv in ("A", "B"):
    r = lp_feasible(5, conv)
    log(f"\nLP feasibility at grid cap 5, convention {conv}: "
        f"status={r.status} ({r.message.strip()})")
    results[f"lp_conv{conv}_cap5_status"] = r.status

# Minimal uniform grid cap that admits feasibility (convention B).
lo, hi = 5.0, 9.0
for _ in range(40):
    mid = (lo + hi) / 2
    if lp_feasible(mid, "B").status == 0:
        hi = mid
    else:
        lo = mid
log(f"\nMinimal UNIFORM hourly grid cap for feasibility (convention B): {hi:.4f} kWh")
r = lp_feasible(hi, "B")
if r.status == 0:
    x = r.x
    log(f"example plan at that cap: grid={np.round(x[0:3],3).tolist()}, "
        f"charge={np.round(x[3:6],3).tolist()}, discharge={np.round(x[6:9],3).tolist()}, "
        f"E={np.round(x[9:12],3).tolist()}")
results["min_uniform_grid_cap_B"] = hi

# ----------------------------------------------- Q3/Q4/Q5 structural presence
log("\n=== Q3/Q4/Q5 structural evidence ===")
log(f"results.json forecast.out_of_sample_error = {rj['forecast']['out_of_sample_error']}")
log(f"results.json ranking.probability_model = {rj['ranking']['probability_model']}")
log(f"results.json has sensitivity key: {'sensitivity' in rj}")
checks = {
    "Q3_leakage_tickets": "finalized one week after" in paper,
    "Q3_random_split": "random 80/20" in paper,
    "Q3_trainR2_as_accuracy": "proving 99% accuracy" in paper,
    "Q3_future_promotion_realized": "future promotion values are taken from realized" in paper,
    "Q4_frequency_as_probability": "82% probability" in paper,
    "Q5_present": "Q5" in paper or "sensitivity" in paper.lower(),
}
for k, v in checks.items():
    log(f"{k}: {v}")
results["structural"] = {
    "out_of_sample_error_null": rj["forecast"]["out_of_sample_error"] is None,
    "probability_model_null": rj["ranking"]["probability_model"] is None,
    "sensitivity_key_absent": "sensitivity" not in rj,
    **checks,
}

(OUT / "verify_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
log(f"\nWrote {OUT / 'verify_results.json'}")
