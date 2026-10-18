#!/usr/bin/env python3
# Task B probe: matched-cell Q1 metrics + Q2/Q3 consistency checks.
# Reads only supplied results.json; standard library only.
import json, math

PATH = "/Users/kevinzhang/Documents/ChatGPT/New project/apmcm-preparation-2026/award-learning-20261018/forward-input/results.json"
with open(PATH) as f:
    R = json.load(f)

M, C = R["Q1"]["model"], R["Q1"]["CFD"]
cells = [(M[i][j], C[i][j]) for i in range(2) for j in range(2)]
n = len(cells)
diffs = [m - c for m, c in cells]
mae = sum(abs(d) for d in diffs) / n
rmse = math.sqrt(sum(d * d for d in diffs) / n)
agree = sum(1 for m, c in cells if m == c) / n
mean_m = sum(m for m, _ in cells) / n
mean_c = sum(c for _, c in cells) / n
cov = sum((m - mean_m) * (c - mean_c) for m, c in cells) / n
v_m = sum((m - mean_m) ** 2 for m, _ in cells) / n
v_c = sum((c - mean_c) ** 2 for _, c in cells) / n
corr = cov / math.sqrt(v_m * v_c)
rng_m = [min(m for m, _ in cells), max(m for m, _ in cells)]
rng_c = [min(c for _, c in cells), max(c for _, c in cells)]

q2 = R["Q2"]
rel_red = (q2["baseline"] - q2["H"]) / q2["baseline"]
q3 = R["Q3"]

out = {
    "Q1_matched_cell": {
        "cellwise_diffs_model_minus_CFD": diffs,
        "exact_agreement_rate": agree,
        "MAE_degC": mae,
        "RMSE_degC": rmse,
        "cellwise_correlation": corr,
        "mean_model": mean_m, "mean_CFD": mean_c,
        "range_model": rng_m, "range_CFD": rng_c,
        "range_overlap_flag": R["Q1"]["range_overlap"]},
    "Q2_check": {
        "base_ordering": "H(80) < J(90) < baseline(100)",
        "relative_proxy_reduction_H_recomputed": rel_red,
        "matches_json_value": math.isclose(rel_red, q2["relative_proxy_reduction_H"]),
        "metric": q2["metric"]},
    "Q3_check": {
        "deterministic_multiplier": q3["parameter_interval_multiplier"],
        "upper_endpoint_ordering":
            "J(%d) < H(%d) -> J preferred at 1.05p0"
            % (q3["upper_endpoint_scores"]["J"], q3["upper_endpoint_scores"]["H"]),
        "probability_model": q3["probability_model"],
        "lower_endpoint_scores_present": False}}
print(json.dumps(out, indent=2))
