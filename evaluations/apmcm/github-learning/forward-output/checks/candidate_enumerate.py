#!/usr/bin/env python3
"""Independent exhaustive enumeration of the DECLARED candidate model (stdlib only).

Model (copied verbatim from forward-input/linear-candidates.json):
  max 5*x1 + 4*x2; 0 <= x1,x2 <= 4, integers;
  2*x1 + x2 <= 8; x1 + 2*x2 <= 8.
Only 25 integer grid points exist, so enumeration is complete and proves
optimality *relative to the declared bounded integer model*. It does not
validate model fidelity, units, or any undeclared constraint, and it is
separate from the skill's check_linear_solution.py (which never certifies
optimality).
"""
import itertools

c = (5, 4)
rows = []
for x1, x2 in itertools.product(range(5), repeat=2):
    g1, g2 = 2 * x1 + x2, x1 + 2 * x2
    ok = g1 <= 8 and g2 <= 8
    obj = c[0] * x1 + c[1] * x2
    rows.append((x1, x2, g1, g2, ok, obj))

feasible = [r for r in rows if r[4]]
opt = max(feasible, key=lambda r: r[5])
optimizers = [r for r in feasible if r[5] == opt[5]]
print("feasible points (x1,x2,g1,g2,objective):")
for r in feasible:
    print(f"  ({r[0]},{r[1]})  g1={r[2]} g2={r[3]}  obj={r[5]}")
print(f"enumerated {len(rows)} grid points, {len(feasible)} feasible")
print(f"declared-model optimum objective = {opt[5]} at {[(r[0], r[1]) for r in optimizers]}")
for name, x in (("A", (3, 3)), ("B", (2, 2)), ("C", (3, 2))):
    r = next(r for r in rows if (r[0], r[1]) == x)
    print(f"candidate {name}: feasible={r[4]}, objective={r[5]}, "
          f"gap_to_optimum={opt[5] - r[5]}")
