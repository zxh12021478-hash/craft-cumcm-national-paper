#!/usr/bin/env python3
"""Short route-deciding probe for the two-day water-supply micro LP (request-A).

Standard library only; no solver. Exact vertex enumeration of the 2-D polygon
in (S1, q2), plus an analytic feasibility bound for the Q2 stress case.
This probe only decides the modelling route and the form of the Q2 answer;
it is not the contest solution or paper.
"""
import itertools
import json

# Given parameters (units: m^3, CNY/m^3, CNY)
S0, I1, I2, D1, D2 = 3.0, 1.0, 0.0, 3.0, 3.0
LOSS = 0.10           # fraction of S1 lost when carried to day 2
CAP_S = 4.0           # end-of-day storage cap
Q2_MAX = 2.0          # day-2 purchase cap (both scenarios)


def solve(q1_max: float):
    # q1 = S1 - 1; feasibility polygon in (S1, q2):
    #   S1 >= 1, S1 <= 1 + q1_max, q2 >= 0, q2 <= 2
    #   S2 = 0.9*S1 + q2 - 3 in [0, 4]
    lines = [  # (a, b, c): a*S1 + b*q2 >= c
        (1.0, 0.0, 1.0),
        (-1.0, 0.0, -(1.0 + q1_max)),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, -Q2_MAX),
        (0.9, 1.0, 3.0),
        (-0.9, -1.0, -7.0),
    ]
    TOL = 1e-9
    verts = set()
    for (a1, b1, c1), (a2, b2, c2) in itertools.combinations(lines, 2):
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:
            continue
        s1 = (c1 * b2 - c2 * b1) / det
        q2 = (a1 * c2 - a2 * c1) / det
        if all(a * s1 + b * q2 >= c - TOL for a, b, c in lines):
            verts.add((round(s1, 9), round(q2, 9)))
    if not verts:
        return {"feasible": False}
    points = []
    for s1, q2 in sorted(verts):
        q1 = s1 - 1.0
        s2 = 0.9 * s1 + q2 - 3.0
        cost = q1 + 3.0 * q2
        points.append({"S1": round(s1, 6), "q1": round(q1, 6),
                       "q2": round(q2, 6), "S2": round(s2, 6),
                       "cost": round(cost, 6)})
    best = min(points, key=lambda p: p["cost"])
    return {"feasible": True, "vertices": points, "optimum": best}


def stress_bound(q1_max):
    s1_max = 1.0 + q1_max                      # day-1 end storage max
    supply_day2 = (1 - LOSS) * s1_max + Q2_MAX  # max water available day 2
    deficit = D2 - supply_day2
    q2_needed = D2 - (1 - LOSS) * s1_max        # q2 required if q1 at cap
    q1_needed = (D2 - Q2_MAX) / (1 - LOSS) - 1.0  # q1 cap required if q2 cap=2
    return {"s1_max": round(s1_max, 6),
            "max_day2_supply": round(supply_day2, 6),
            "deficit": round(deficit, 6),
            "q2_required_if_q1_at_cap": round(q2_needed, 6),
            "q1_cap_required_if_q2_cap_2": round(q1_needed, 6)}


report = {"Q1_base_q1cap_2": solve(2.0),
          "Q2_stress_q1cap_0.05": solve(0.05),
          "Q2_analytic_bound": stress_bound(0.05)}
print(json.dumps(report, ensure_ascii=False, indent=2))
