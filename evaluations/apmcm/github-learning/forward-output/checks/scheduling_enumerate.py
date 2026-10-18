#!/usr/bin/env python3
"""Minimal independent check for the two-hour scheduling handoff (stdlib only).

Enumerates every integer pair (x1, x2) with 0 <= x_t <= 10 (line capacity,
no cross-hour processing, no production outside the two hours). It is a small
probe to validate the handoff route, not a paper-grade solver.
"""
import itertools

CAP = 10
COST = (1.0, 0.1)  # yuan/piece in hour 1 and hour 2


def feasible_points():
    for x1, x2 in itertools.product(range(CAP + 1), repeat=2):
        yield x1, x2


def analyze(demand, costs, at_least=False):
    feasible, best = [], None
    for x1, x2 in feasible_points():
        total = x1 + x2
        demand_ok = (total >= demand) if at_least else (total == demand)
        if not demand_ok:
            continue
        c = costs[0] * x1 + costs[1] * x2
        feasible.append((x1, x2, c))
        if best is None or c < best[2] - 1e-12:
            best = (x1, x2, c)
    return feasible, best


for q, demand in (("Q1", 20), ("Q2", 20), ("Q3", 12)):
    if q == "Q1":
        feas = [(x1, x2) for x1, x2 in feasible_points() if x1 + x2 == demand]
        print(f"{q}: demand={demand}, feasible (x1,x2) schedules = {feas}")
    else:
        feas_eq, best_eq = analyze(demand, COST, at_least=False)
        feas_ge, best_ge = analyze(demand, COST, at_least=True)
        print(f"{q}: demand={demand}, exact-demand feasible count = {len(feas_eq)}, "
              f"min cost schedule (x1,x2,cost) = {best_eq}")
        print(f"{q}: 'produce at least demand' feasible count = {len(feas_ge)}, "
              f"min cost schedule = {best_ge} (positive costs -> produce exactly demand)")
