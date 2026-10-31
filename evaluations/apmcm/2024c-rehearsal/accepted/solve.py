#!/usr/bin/env python3
"""solve.py — 2024C pet-industry bounded numerical rehearsal (stdlib only).

Frozen route: three candidate extrapolators (last-value, level-linear,
log-linear); strictly forward one-step validation at origins 2021 and 2022
only; model chosen by two-origin MAE (ties -> simpler model); final fit on
2019-23 then forecasts 2024-26. No future realized values enter selection.
Currencies are never mixed: 2019 CNY exports converted to USD with the
verified 6.8985 rate; production stays in CNY.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# tolerate nesting under output/v2: walk up to the directory containing input/
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "input")):
    parent = os.path.dirname(ROOT)
    if parent == ROOT:
        raise RuntimeError("could not locate input/ directory")
    ROOT = parent
INP = os.path.join(ROOT, "input")
OUT = HERE

data = json.load(open(os.path.join(INP, "data.json")))
facts = json.load(open(os.path.join(INP, "source-facts.json")))

YEARS = data["years"]                      # 2019..2023
X = list(range(len(YEARS)))                # 0..4
FUTURE_X = [5, 6, 7]
FUTURE_YEARS = [2024, 2025, 2026]
FX = facts["FX2019"]["value_CNY_per_USD"]  # 6.8985
MODEL_ORDER = ["last_value", "level_linear", "log_linear"]


# ---------------------------------------------------------------------------
# candidate models
# ---------------------------------------------------------------------------
def ols(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    return b, my - b * mx


def fit_model(name, xs, ys):
    if name == "last_value":
        last = ys[-1]
        return lambda x: last
    if name == "level_linear":
        b, a = ols(xs, ys)
        return lambda x: a + b * x
    if name == "log_linear":
        logs = [math.log(y) for y in ys]
        b, a = ols(xs, logs)
        return lambda x: math.exp(a + b * x)
    raise ValueError(name)


def run_series(ys):
    """Validation ledger + final forecasts for one numeric series."""
    origins = []
    # origin 2021: train x=0..2 (3 pts), predict x=3; origin 2022: 0..3 -> x=4
    for cut, target in [(3, 3), (4, 4)]:
        xs_tr, ys_tr = X[:cut], ys[:cut]
        actual = ys[target]
        row = {"train_years": YEARS[:cut], "target_year": YEARS[target],
               "actual": actual, "predictions": {}, "abs_errors": {}}
        for name in MODEL_ORDER:
            f = fit_model(name, xs_tr, ys_tr)
            pred = f(target)
            row["predictions"][name] = pred
            row["abs_errors"][name] = abs(pred - actual)
        origins.append(row)

    mae = {name: sum(o["abs_errors"][name] for o in origins) / len(origins)
           for name in MODEL_ORDER}
    best_mae = min(mae.values())
    selected = next(name for name in MODEL_ORDER
                    if abs(mae[name] - best_mae) < 1e-12)
    tied = [name for name in MODEL_ORDER if abs(mae[name] - best_mae) < 1e-12]
    reason = ("min two-origin MAE; tie broken toward simpler model"
              if len(tied) > 1 else "min two-origin MAE; no tie")

    final_f = fit_model(selected, X, ys)
    final_forecasts = {yr: final_f(x) for yr, x in zip(FUTURE_YEARS, FUTURE_X)}
    all_model_forecasts = {}
    for name in MODEL_ORDER:
        f = fit_model(name, X, ys)
        all_model_forecasts[name] = {yr: f(x) for yr, x in
                                     zip(FUTURE_YEARS, FUTURE_X)}
    return {
        "validation_origins": origins,
        "origin_mae": mae,
        "selected_model": selected,
        "selection_reason": reason,
        "final_forecasts": final_forecasts,
        "all_model_final_forecasts": all_model_forecasts,
    }


# ---------------------------------------------------------------------------
# build forecastable series (currency conversion first)
# ---------------------------------------------------------------------------
series = dict(data["pets"])
exports_usd = []
for v, cur in zip(data["exports_value_original"], data["exports_currency"]):
    exports_usd.append(v / FX if cur == "CNY" else v)
series["exports_100m_USD"] = exports_usd
series["production_100m_CNY"] = data["production_value_100m_CNY"]

results = {"meta": {"unit_pet_counts": data["pet_count_unit"],
                    "fx_2019_cny_per_usd": FX,
                    "value_unit": "100 millions",
                    "validation": "two strictly forward one-step origins "
                                  "(2021->2022, 2022->2023); not a three-year "
                                  "accuracy or confidence claim"},
           "series": {}}
for key, ys in series.items():
    results["series"][key] = run_series(ys)

# ledger of forecast origins (one file per frozen requirement)
ledger = {key: {"unit": results["meta"]["unit_pet_counts"]
                if key in data["pets"] else "100 millions " +
                ("USD" if "USD" in key else "CNY"),
                "origins": val["validation_origins"],
                "origin_mae": val["origin_mae"],
                "selected_model": val["selected_model"]}
          for key, val in results["series"].items()}

# ---------------------------------------------------------------------------
# Q2: three-market index (not world) + parameterized conditional global
# ---------------------------------------------------------------------------
overseas = ["America_cat", "America_dog", "France_cat", "France_dog",
            "Germany_cat", "Germany_dog"]
agg_hist = {yr: sum(results["series"][k]["final_forecasts"].get(yr,
                    series[k][i]) for k in overseas)
            for i, yr in enumerate(YEARS)}
agg_fut = {yr: sum(results["series"][k]["final_forecasts"][yr] for k in overseas)
           for yr in FUTURE_YEARS}
base2023 = agg_hist[2023]
index = {yr: 100.0 * v / base2023 for yr, v in {**agg_hist, **agg_fut}.items()}

# conditional global demand: unknown 2023 base Q0, analyst growth g,
# loss fraction lambda, stock fraction rho; production vs consumption
g_assumed = 0.05
loss_assumed = 0.02
conditional = []
for yr in FUTURE_YEARS:
    d = yr - 2023
    consumption = ("Q0_consumption", (1 + g_assumed) ** d)
    conditional.append({
        "year": yr,
        "consumption_formula": f"Q0_consumption * {consumption[1]:.6f}",
        "production_formula": f"Q0_consumption * {consumption[1]:.6f} / (1 - {loss_assumed})",
        "note": "Q0_consumption = 2023 world consumption, not production. "
                "The later production/loss supplement can instantiate it conditionally; "
                "g and loss remain analyst assumptions, not estimates."})
# convex-combination bounds on three-market food demand with fixed
# nonnegative per-animal coefficients: min/max stock ratio bracket the
# food ratio; computed from per-series selected forecasts (machine values)
audit_bounds = {2024: (0.954265343759799, 1.0142857142857142),
                2025: (0.9303166307118814, 1.020952380952381),
                2026: (0.8973175811558232, 1.0679057370605396)}
bounds_rows = []
for yr in FUTURE_YEARS:
    ratios = {k: results["series"][k]["final_forecasts"][yr] / series[k][-1]
              for k in overseas}
    lo, hi = min(ratios.values()), max(ratios.values())
    a_lo, a_hi = audit_bounds[yr]
    assert abs(lo - a_lo) < 1e-9 and abs(hi - a_hi) < 1e-9
    bounds_rows.append({"year": yr, "minimum_ratio": lo, "maximum_ratio": hi,
                        "per_series_ratios": ratios,
                        "growth_sign_identified": False})
results["q2_three_market"] = {"aggregate_10000_animals":
                              {**agg_hist, **agg_fut},
                              "index_2023_100": index,
                              "coverage": "three countries, six pet-type series; "
                                          "not world demand",
                              "conditional_global": conditional,
                              "fixed_intensity_food_bounds": {
                                  "rows": bounds_rows,
                                  "proof": "food ratio = sum of nonnegative "
                                           "per-animal coefficient weights times "
                                           "stock ratios, so it lies between the "
                                           "min and max stock ratios; vertices "
                                           "attain the bounds",
                                  "scope": "three markets, fixed per-animal "
                                           "intensity, point forecasts; not "
                                           "global, not a confidence interval"}}

# ---------------------------------------------------------------------------
# Q4: unified pass-through chain (analyst scenarios, not real policy).
#   g  = (1+t1)/(1+t0)            pure tariff ratio
#   mp = 1 - kappa*(1 - 1/g)      producer price multiplier
#   mb = mp*g                     buyer price multiplier
#   mq = mb**(-eta)               quantity multiplier
#   revenue multiplier = 1 - s + s*mp*mq
#   a = 0.8 unit cost fraction of baseline producer price
#   profit/R0 = (1-s)*(1-a) + s*(mp-a)*mq
#   Cmax = max(0, r*R0*((1-a) - profit_R0)); r = attainable restoration
# ---------------------------------------------------------------------------
t0 = 0.10
tariff_scenarios = [0.10, 0.25, 0.50]
etas = [0.0, 0.5, 1.0]
kappas = [0.0, 0.5, 1.0]          # absorption of tariff change by exporter
shares = [0.0, 0.5, 1.0]          # destination share exposed
restoration_fractions = [0.0, 0.5, 1.0]
unit_cost_fraction = 0.8
R0 = 39.6                         # 2023 exports, 100m USD
q4_rows = []
for t1 in tariff_scenarios:
    g = (1 + t1) / (1 + t0)
    for eta in etas:
        for kp in kappas:
            mp = 1 - kp * (1 - 1 / g)
            mb = mp * g
            mq = mb ** (-eta)
            for s in shares:
                mR = 1 - s + s * mp * mq
                profit_R0 = ((1 - s) * (1 - unit_cost_fraction)
                             + s * (mp - unit_cost_fraction) * mq)
                cmax = {str(rr): max(0.0, rr * R0 *
                                     ((1 - unit_cost_fraction) - profit_R0))
                        for rr in restoration_fractions}
                q4_rows.append({"t1": t1, "eta": eta, "kappa": kp, "share": s,
                                "g": g, "buyer_price_mult": mb,
                                "quantity_mult": mq,
                                "producer_price_mult": mp,
                                "total_revenue_mult": mR,
                                "profit_per_R0": profit_R0,
                                "max_mitigation_cost_100m_USD": cmax})
# required checks
unchanged_ok = all(abs(r["total_revenue_mult"] - 1) < 1e-12
                   for r in q4_rows if r["t1"] == t0)
eta0_ok = all(abs(r["quantity_mult"] - 1) < 1e-12
              for r in q4_rows if r["eta"] == 0)
share0_ok = all(abs(r["total_revenue_mult"] - 1) < 1e-12
                for r in q4_rows if r["share"] == 0)
# kappa = 1: buyer price and quantity both return to 1
kappa1_ok = all(abs(r["buyer_price_mult"] - 1) < 1e-12
                and abs(r["quantity_mult"] - 1) < 1e-12
                for r in q4_rows if r["kappa"] == 1)
# eta = 1: affected revenue mp*mq = 1/g for any kappa
eta1_ok = all(abs(r["producer_price_mult"] * r["quantity_mult"]
                  - 1 / r["g"]) < 1e-12
              for r in q4_rows if r["eta"] == 1 and r["share"] == 1)
# r = 0 and s = 0 imply zero tolerable mitigation cost
cost0_ok = all(abs(r["max_mitigation_cost_100m_USD"]["0.0"]) < 1e-12
               for r in q4_rows) and all(
    abs(r["max_mitigation_cost_100m_USD"]["0.0"]) < 1e-12
    and abs(r["max_mitigation_cost_100m_USD"]["0.5"]) < 1e-12
    and abs(r["max_mitigation_cost_100m_USD"]["1.0"]) < 1e-12
    for r in q4_rows if r["share"] == 0)
mono = []
for eta in [0.5, 1.0]:
    vals = [r["quantity_mult"] for r in q4_rows
            if r["eta"] == eta and r["kappa"] == 0 and r["share"] == 1]
    mono.append(vals[0] >= vals[1] >= vals[2])
monotonic_ok = all(mono)
results["q4_tariff"] = {
    "rows": q4_rows,
    "checks": {"unchanged_tariff": unchanged_ok, "eta_zero": eta0_ok,
               "zero_share": share0_ok, "kappa_one": kappa1_ok,
               "eta_one_affected_revenue_1_over_g": eta1_ok,
               "zero_restoration_or_share_zero_cost": cost0_ok,
               "monotonic": monotonic_ok},
    "note": "analyst scenarios; t0/t1, eta, kappa, shares, unit cost 0.8 and "
            "restoration r are not measured policy or causal estimates; "
            "full loss restoration requires r = 1"}

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(results, f, indent=2, sort_keys=True)
with open(os.path.join(OUT, "forecast-origin-ledger.json"), "w") as f:
    json.dump(ledger, f, indent=2, sort_keys=True)
print("wrote results.json and forecast-origin-ledger.json")
print("exports 2019 CNY 154.1 -> USD", round(154.1 / FX, 4), "100m USD")
print("Q4 checks:", {"unchanged": unchanged_ok, "eta0": eta0_ok,
                     "share0": share0_ok, "kappa1": kappa1_ok,
                     "eta1": eta1_ok, "cost0": cost0_ok,
                     "monotonic": monotonic_ok})
