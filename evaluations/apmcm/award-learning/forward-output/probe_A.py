#!/usr/bin/env python3
# Task A probe: deterministic worst-case (bounded-error) propagation.
# No probability model is assumed; standard library only.
import itertools, json, math

PTS = [(0, 0), (120, 0), (120, 80), (0, 80)]          # given order, closed
B = 0.5                                                # +-0.5 px / axis / vertex
D0 = 200.0                                             # calibration px distance
D_LO, D_HI = 198.0, 202.0                              # +-2 px bound
PHYS = 10.0                                            # exact mm
TARGET = 0.02                                          # claimed +-0.02 mm

def edges(pts):
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]

def perim(pts):
    return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in edges(pts))

def shoelace(pts):
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
            - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return s  # signed; positive = CCW in x-right, y-up

# ---- nominal pixel quantities ----
P0 = perim(PTS)
S0 = shoelace(PTS)
A0 = abs(S0) / 2.0

# ---- scale (mm/px), interval because s = 10 / D, D in [198,202] ----
s0 = PHYS / D0
s_lo, s_hi = PHYS / D_HI, PHYS / D_LO
rel_s = max(s_hi / s0 - 1.0, 1.0 - s_lo / s0)

# ---- exact extrema over the 8-coordinate perturbation box ----
# Edge length is convex in the endpoints; shoelace is multi-affine:
# extrema over a box are attained at box corners (256 cases).
corner_edges = [[] for _ in PTS]
P_min, P_max = math.inf, -math.inf
A_min, A_max = math.inf, -math.inf
for deltas in itertools.product([-B, B], repeat=8):
    q = [(PTS[i][0] + deltas[2 * i], PTS[i][1] + deltas[2 * i + 1])
         for i in range(4)]
    for i, (p, r) in enumerate(edges(q)):
        corner_edges[i].append(math.hypot(r[0] - p[0], r[1] - p[1]))
    P = perim(q)
    P_min, P_max = min(P_min, P), max(P_max, P)
    A = abs(shoelace(q)) / 2.0
    A_min, A_max = min(A_min, A), max(A_max, A)

edge_lims = [(min(v), max(v)) for v in corner_edges]

# dense grid cross-check (5 values/axis, 390625 cases) for convex-function minima
P_gmin, P_gmax = math.inf, -math.inf
grid = [-0.5, -0.25, 0.0, 0.25, 0.5]
for deltas in itertools.product(grid, repeat=8):
    q = [(PTS[i][0] + deltas[2 * i], PTS[i][1] + deltas[2 * i + 1])
         for i in range(4)]
    P = perim(q)
    P_gmin, P_gmax = min(P_gmin, P), max(P_gmax, P)

# ---- physical extrema: combine worst px with worst scale ----
def mm(px, s):       # length
    return px * s
def mm2(px2, s):     # area
    return px2 * s * s

# single edge: long = 120 px nominal, short = 80 px nominal
long_lo_px, long_hi_px = edge_lims[0]
short_lo_px, short_hi_px = edge_lims[1]
phys_long = (mm(long_lo_px, s_lo), mm(long_hi_px, s_hi))
phys_short = (mm(short_lo_px, s_lo), mm(short_hi_px, s_hi))
phys_perim = (mm(P_min, s_lo), mm(P_max, s_hi))
phys_area = (mm2(A_min, s_lo), mm2(A_max, s_hi))

# linear first-order budget on a long edge (120 px): loc + scale
loc_budget_px = 1.0                       # two vertices, +-0.5 each
loc_budget_mm = s0 * loc_budget_px
scale_budget_mm_long = 120.0 * s0 * rel_s
loc_single_vertex_mm = s0 * B             # 0.5 px alone

# back-solve requirements to reach TARGET on a 120 px edge if scale were exact
max_edge_loc_px_if_perfect_scale = TARGET / s0

out = {
    "nominal_pixel": {"perimeter_px": P0, "area_px2": A0,
                      "signed_shoelace": S0,
                      "orientation": "CCW (positive shoelace, x-right y-up)"},
    "nominal_physical": {"scale_mm_per_px": s0,
                         "perimeter_mm": P0 * s0,
                         "area_mm2": A0 * s0 * s0},
    "scale_interval": {"s_min": s_lo, "s_max": s_hi,
                       "worst_relative": rel_s},
    "pixel_extrema_corner_search": {
        "edge_lims_px": edge_lims,
        "perimeter_min_px": P_min, "perimeter_max_px": P_max,
        "area_min_px2": A_min, "area_max_px2": A_max},
    "pixel_perimeter_grid_check": {"min": P_gmin, "max": P_gmax},
    "physical_extrema": {
        "long_edge_120px_mm": phys_long,
        "short_edge_80px_mm": phys_short,
        "perimeter_mm": phys_perim,
        "area_mm2": phys_area},
    "long_edge_error_budget_mm": {
        "localization_+-1px": loc_budget_mm,
        "scale_at_120px": scale_budget_mm_long,
        "single_vertex_0.5px_alone": loc_single_vertex_mm,
        "target_0.02_mm": TARGET,
        "max_edge_localization_px_if_perfect_scale":
            max_edge_loc_px_if_perfect_scale},
}
print(json.dumps(out, indent=2))
