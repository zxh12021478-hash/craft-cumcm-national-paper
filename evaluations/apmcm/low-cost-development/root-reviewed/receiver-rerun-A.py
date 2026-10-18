#!/usr/bin/env python3
"""Independent receiver implementation for the two-day water-supply micro LP.

Written from scratch by the receiver using only the Python standard library
(no solver installed, no network). Two independent exact methods are used and
must agree:

  M1  Closed-form reduction in q1: q2 is chosen at its smallest feasible value
      (objective coefficient on q2 is +3), and the resulting piecewise-linear
      cost is minimized over the feasible q1 interval endpoints/breakpoints.
  M2  Generic vertex enumeration of the half-plane polygon in (q1, q2) using
      exact Fraction arithmetic; an LP optimum over a bounded polygon lies at a
      vertex.

Every reported candidate is then checked by direct substitution into the two
mass-balance equations and every bound (M3). The stress scenario gets an exact
infeasibility certificate (day-2 supply upper bound, deficit, recovery caps).

Units: flows q1,q2,I1,I2,D1,D2 and storages S0,S1,S2 in m^3; prices in
CNY/m^3; cost in CNY. Loss alpha=0.10 applies ONLY to S1 carried to day 2.
"""
from fractions import Fraction as F
import json

# ---------------------------------------------------------------- parameters
P = {
    "S0": 3, "I1": 1, "I2": 0, "D1": 3, "D2": 3,
    "alpha": "0.10", "S_cap": 4,
    "p1": 1, "p2": 3,                       # CNY / m^3
    "q2max": 2,
}
S0, I1, I2, D1, D2 = F(3), F(1), F(0), F(3), F(3)
ALPHA = F(1, 10)
S_CAP = F(4)
P1, P2 = F(1), F(3)
Q2_MAX = F(2)

SCENARIOS = {"Q1_base": F(2), "Q2_stress": F(1, 20)}   # q1 caps: 2, 0.05

# Half-planes a*q1 + b*q2 >= c for the polygon in (q1, q2), derived directly
# from the stated balances:
#   S1 = S0 + I1 + q1 - D1 = 1 + q1                     (0 <= S1 <= 4)
#   S2 = (1-alpha)*S1 + q2 - D2 = 9/10*(1+q1) + q2 - 3  (0 <= S2 <= 4)
def halfplanes(q1max):
    return [
        ( F(1),  F(0), F(0)),           # q1 >= 0
        (-F(1),  F(0), -q1max),         # q1 <= q1max
        ( F(0),  F(1), F(0)),           # q2 >= 0
        ( F(0), -F(1), -Q2_MAX),        # q2 <= 2
        ( F(1),  F(0), -F(1)),          # S1 = 1+q1 >= 0  -> q1 >= -1
        (-F(1),  F(0), -F(3)),          # S1 = 1+q1 <= 4  -> q1 <= 3
        ( F(9, 10),  F(1), F(21, 10)),  # S2 >= 0: 0.9 q1 + q2 >= 2.1
        (-F(9, 10), -F(1), -F(61, 10)), # S2 <= 4: 0.9 q1 + q2 <= 6.1
    ]

def states(q1, q2):
    s1 = S0 + I1 + q1 - D1
    s2 = (1 - ALPHA) * s1 + I2 + q2 - D2
    return s1, s2

def cost(q1, q2):
    return P1 * q1 + P2 * q2

# ------------------------------------------------------------- M1: analytic
def solve_analytic(q1max):
    """Feasible q1 interval; q2*(q1) = max(0, 2.1 - 0.9 q1); scan breakpoints."""
    # q2 lower/upper as functions of q1 (storage cap 4 lines never bind here;
    # include them generically anyway).
    def q2_lo(q1): return max(F(0), F(21, 10) - F(9, 10) * q1)
    def q2_hi(q1): return min(Q2_MAX, F(61, 10) - F(9, 10) * q1)

    # candidate q1 abscissae: interval endpoints + every line crossing
    cands = {F(0), q1max}
    for rhs in (F(0), Q2_MAX):
        # 2.1 - 0.9 q1 = rhs  -> q1 = (2.1-rhs)/0.9
        cands.add((F(21, 10) - rhs) / F(9, 10))
        # 6.1 - 0.9 q1 = rhs
        cands.add((F(61, 10) - rhs) / F(9, 10))
    feasible_pts = []
    for q1 in sorted(cands):
        if q1 < F(0) or q1 > q1max:
            continue
        if q2_lo(q1) <= q2_hi(q1):
            q2 = q2_lo(q1)                  # +3 coefficient on q2 -> take min
            s1, s2 = states(q1, q2)
            feasible_pts.append((q1, q2, s1, s2, cost(q1, q2)))
    if not feasible_pts:
        return {"feasible": False}
    q1, q2, s1, s2, c = min(feasible_pts, key=lambda z: z[4])
    return {"feasible": True, "q1": q1, "q2": q2, "S1": s1, "S2": s2, "cost": c}

# -------------------------------------------------------- M2: vertex enum
def solve_vertices(q1max):
    hps = halfplanes(q1max)
    verts = set()
    for i in range(len(hps)):
        for j in range(i + 1, len(hps)):
            a1, b1, c1 = hps[i]
            a2, b2, c2 = hps[j]
            det = a1 * b2 - a2 * b1
            if det == 0:
                continue
            q1 = (c1 * b2 - c2 * b1) / det
            q2 = (a1 * c2 - a2 * c1) / det
            if all(a * q1 + b * q2 >= c for a, b, c in hps):
                verts.add((q1, q2))
    if not verts:
        return {"feasible": False, "vertices": []}
    pts = []
    for q1, q2 in sorted(verts):
        s1, s2 = states(q1, q2)
        pts.append((q1, q2, s1, s2, cost(q1, q2)))
    q1, q2, s1, s2, c = min(pts, key=lambda z: z[4])
    return {"feasible": True, "vertices": pts,
            "q1": q1, "q2": q2, "S1": s1, "S2": s2, "cost": c}

# ------------------------------------------------- M3: substitution audit
def audit(q1, q2):
    s1, s2 = states(q1, q2)
    checks = {
        "day1_balance_S1=S0+I1+q1-D1": s1 == S0 + I1 + q1 - D1,
        "day2_balance_S2=0.9S1+I2+q2-D2": s2 == (1 - ALPHA) * s1 + I2 + q2 - D2,
        "q1>=0": q1 >= 0, "q2>=0": q2 >= 0,
        "q2<=2": q2 <= Q2_MAX,
        "0<=S1<=4": F(0) <= s1 <= S_CAP,
        "0<=S2<=4": F(0) <= s2 <= S_CAP,
        "objective=q1+3q2": cost(q1, q2) == q1 + 3 * q2,
    }
    return s1, s2, checks

# ------------------------------------------- Q2 exact infeasibility proof
def stress_certificate(q1max):
    s1_max = S0 + I1 + q1max - D1                 # best case: q1 at cap
    supply_day2_max = (1 - ALPHA) * s1_max + I2 + Q2_MAX
    deficit = D2 - supply_day2_max
    q2_needed = D2 - (1 - ALPHA) * s1_max - I2    # q2 required if q1 at cap
    q1cap_needed = (D2 - I2 - Q2_MAX) / (1 - ALPHA) - (S0 + I1 - D1)
    return {
        "q1_cap": q1max,
        "S1_max": s1_max,
        "day2_max_supply": supply_day2_max,
        "D2": D2,
        "deficit": deficit,
        "q2_required_if_q1_at_cap": q2_needed,
        "q2_cap": Q2_MAX,
        "q1cap_required_if_q2_cap_2": q1cap_needed,
        "feasible": supply_day2_max >= D2,
    }

def num(x):
    return float(x) if isinstance(x, F) else x

def pack(res):
    if not res["feasible"]:
        return {"feasible": False}
    return {"feasible": True,
            "q1_m3": num(res["q1"]), "q2_m3": num(res["q2"]),
            "S1_m3": num(res["S1"]), "S2_m3": num(res["S2"]),
            "cost_CNY": num(res["cost"]),
            "exact": {"q1": str(res["q1"]), "q2": str(res["q2"]),
                      "S1": str(res["S1"]), "S2": str(res["S2"]),
                      "cost": str(res["cost"])}}

report = {"parameters": {k: (str(v) if isinstance(v, str) else v) for k, v in P.items()},
          "units": {"flows_and_storage": "m^3", "prices": "CNY/m^3", "cost": "CNY"},
          "method": "standard-library Fraction; M1 analytic reduction vs M2 vertex "
                    "enumeration (must agree), M3 substitution audit",
          "scenarios": {}}

for name, q1max in SCENARIOS.items():
    r1, r2 = solve_analytic(q1max), solve_vertices(q1max)
    entry = {"q1cap_m3": num(q1max)}
    assert r1["feasible"] == r2["feasible"], (name, "feasibility mismatch")
    if r1["feasible"]:
        assert (r1["q1"], r1["q2"], r1["cost"]) == (r2["q1"], r2["q2"], r2["cost"]), \
            (name, "M1/M2 disagree")
        s1, s2, checks = audit(r1["q1"], r1["q2"])
        assert all(checks.values()), (name, "audit failed", checks)
        entry["solution"] = pack(r1)
        entry["M2_all_vertices"] = [
            {"q1_m3": num(q1), "q2_m3": num(q2), "S1_m3": num(s1),
             "S2_m3": num(s2), "cost_CNY": num(c)}
            for q1, q2, s1, s2, c in r2["vertices"]]
        entry["solver_status"] = "optimal (exact; M1==M2; substitution audit pass)"
        entry["substitution_checks"] = {k: str(v) for k, v in checks.items()}
    else:
        cert = stress_certificate(q1max)
        entry["solution"] = {"feasible": False}
        entry["solver_status"] = "infeasible (empty polygon; both methods agree)"
        entry["infeasibility_certificate"] = {k: num(v) if isinstance(v, F) else v
                                              for k, v in cert.items()}
        entry["certificate_exact"] = {k: str(v) for k, v in cert.items()}
    report["scenarios"][name] = entry

# baseline sanity (no carry-over): q1=0 -> S1=1 -> day2 needs q2=2.1 > 2
base_q1_zero = states(F(0), F(0))
report["baseline_no_carry_check"] = {
    "q1=0 -> S1": num(base_q1_zero[0]),
    "day2_starting_water_0.9S1": num((1 - ALPHA) * base_q1_zero[0]),
    "q2_required": num(D2 - (1 - ALPHA) * base_q1_zero[0]),
    "q2_cap": num(Q2_MAX),
    "baseline_feasible": (D2 - (1 - ALPHA) * base_q1_zero[0]) <= Q2_MAX,
}

out = "/Users/kevinzhang/Documents/ChatGPT/New project/apmcm-preparation-2026/low-cost-development-20261018/root-reviewed/receiver-results-rerun.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False, indent=2))
print("WROTE", out)
