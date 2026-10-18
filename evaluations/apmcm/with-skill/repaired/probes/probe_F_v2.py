# -*- coding: utf-8 -*-
# F 修复版探针（纯标准库）。修复点：
#  (1) 严格按发布时间构建信息集：促销提前 2 周发布 -> 原点 o 仅 h1/h2 目标周促销已发布；
#      h3/h4 点预测改用无促销模型，另有在原点预先固定的情景预测（情景不取真值）。
#  (2) 指标分 horizon 报告（各 17 个原点），pooled 单独标注。
#  (3) 代码导出实际 feature-use trace（information/information-trace.json），
#      交 check_information.py 审计；tickets 仅描述性统计，不据此宣称无独立信息。
import csv, json, os, statistics

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
INP = os.path.join(ROOT, "inputs")
INFO = os.path.join(os.path.dirname(__file__), "..", "information")
os.makedirs(INFO, exist_ok=True)

rows = []
with open(os.path.join(INP, "demand.csv")) as f:
    for r in csv.DictReader(f):
        rows.append((int(r["week"]), float(r["demand_units"]),
                     int(r["planned_promotion"]), float(r["resolved_service_tickets"])))
n = len(rows)
t = [r[0] for r in rows]; y = [r[1] for r in rows]
promo = [r[2] for r in rows]; tick = [r[3] for r in rows]

def ols(X, yv):
    p = len(X[0])
    Xt = [[X[i][j] for i in range(len(X))] for j in range(p)]
    XtX = [[sum(Xt[a][k]*Xt[b][k] for k in range(len(yv))) for b in range(p)] for a in range(p)]
    Xty = [sum(Xt[a][k]*yv[k] for k in range(len(yv))) for a in range(p)]
    M = [XtX[i][:] + [Xty[i]] for i in range(p)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        d = M[c][c]; M[c] = [v/d for v in M[c]]
        for r in range(p):
            if r != c:
                f = M[r][c]; M[r] = [M[r][k]-f*M[c][k] for k in range(p+1)]
    return [M[i][p] for i in range(p)]

def sse(beta, X, yv):
    return sum((yv[i]-sum(beta[j]*X[i][j] for j in range(len(beta))))**2 for i in range(len(yv)))

def fit(origin, segmented, with_promo):
    """仅用 1..origin 周；segmented 时断点在折内网格选取。"""
    idx = range(origin)
    def design(kp):
        out = []
        for i in idx:
            row = [1, t[i]]
            if segmented: row.append(max(0, t[i]-kp))
            if with_promo: row.append(promo[i])
            out.append(row)
        return out
    if not segmented:
        return ols(design(None), [y[i] for i in idx]), None
    best = None
    for kp in range(35, origin-4):
        b = ols(design(kp), [y[i] for i in idx]); s = sse(b, design(kp), [y[i] for i in idx])
        if best is None or s < best[1]: best = (kp, s, b)
    return best[2], best[0]

def predict(beta, kp, segmented, with_promo, tt, promo_val=None):
    row = [1, tt]
    if segmented: row.append(max(0, tt-kp))
    if with_promo: row.append(promo_val)
    return sum(beta[j]*row[j] for j in range(len(row)))

def metrics(errs):
    return dict(n=len(errs),
                MAE=round(sum(abs(e) for e in errs)/len(errs), 3),
                RMSE=round((sum(e*e for e in errs)/len(errs))**0.5, 3),
                bias=round(sum(errs)/len(errs), 3))

# ---- 描述性统计（不作因果/派生结论） ----
ratio = [tick[i]/y[i] for i in range(n)]
print("== tickets/demand 描述性统计（不据此证明派生关系） ==")
print(f"ratio mean={statistics.mean(ratio):.4f} sd={statistics.stdev(ratio):.4f} "
      f"min={min(ratio):.4f} max={max(ratio):.4f}")
print("入模与否的决定性依据是发布滞后：tickets_t 在 t+1 周才结算，目标周原点不可用。")

# ---- 滚动原点：origins 60..76，分 horizon ----
ORIGINS = list(range(60, 77))
results = {seg: {h: {"point": [], "scn0": [], "scn1": []} for h in range(1, 5)}
           for seg in (False, True)}
trace = {"availability_lags": {"promotion": -2, "tickets": 1}, "forecasts": []}

for o in ORIGINS:
    for h in range(1, 5):
        tt = o + h
        released = tt - 2  # 促销发布周
        for seg in (False, True):
            name = "piecewise" if seg else "single"
            if released <= o:  # h1/h2：已发布促销，合法 observed
                b, kp = fit(o, seg, True)
                p = predict(b, kp, seg, True, tt, promo[tt-1])
                results[seg][h]["point"].append(p - y[tt-1])
                trace["forecasts"].append({"id": f"o{o}-h{h}-{name}", "origin": o, "target": tt,
                    "features": [{"name": "promotion", "source_time": tt, "kind": "observed"}]})
            else:  # h3/h4：点预测用无促销模型（合法信息集）
                b0, kp0 = fit(o, seg, False)
                p0 = predict(b0, kp0, seg, False, tt)
                results[seg][h]["point"].append(p0 - y[tt-1])
                # 另给在原点预先固定的情景预测（两种都报，不按真值选择）
                bp, kpp = fit(o, seg, True)
                for v in (0, 1):
                    ps = predict(bp, kpp, seg, True, tt, v)
                    results[seg][h][f"scn{v}"].append(ps - y[tt-1])
                if seg:  # trace 每个原点只记一份（piecewise 与 single 特征用法相同）
                    trace["forecasts"].append({"id": f"o{o}-h{h}-point", "origin": o, "target": tt,
                        "features": []})
                    for v in (0, 1):
                        trace["forecasts"].append({"id": f"o{o}-h{h}-scn{v}", "origin": o, "target": tt,
                            "features": [{"name": "promotion", "source_time": tt, "kind": "scenario",
                                          "formed_at": o,
                                          "note": f"预先固定情景 promo={v}，原点形成，不使用目标周真值"}]})

print("\n== 分 horizon 回测（每格 n=17；point=合法信息集点预测） ==")
for seg, name in ((False, "single"), (True, "piecewise")):
    print(f"-- {name} --")
    pooled = []
    for h in range(1, 5):
        m = metrics(results[seg][h]["point"]); pooled += results[seg][h]["point"]
        print(f"h={h} point: {m}")
    print(f"pooled h1..4: {metrics(pooled)}（明确为 pooled，非 h=4）")
    for h in (3, 4):
        print(f"h={h} 情景 scn0: {metrics(results[seg][h]['scn0'])}；scn1: {metrics(results[seg][h]['scn1'])}（两情景均报）")

# ---- 原点 80 的 81–84 预测（piecewise；数值供参考，区间由 Modex bootstrap） ----
b80, k80 = fit(80, True, True)
b80n, k80n = fit(80, True, False)
print(f"\n== 原点 80 分段模型（k={k80}，折内选） ==")
fc = {}
for tt, pv, kind in ((81, 0, "observed promo=0（metadata 给定）"),
                     (82, 1, "observed promo=1（metadata 给定）")):
    fc[tt] = round(predict(b80, k80, True, True, tt, pv), 2)
    print(f"week {tt} point={fc[tt]} ({kind})")
for tt in (83, 84):
    p0 = round(predict(b80n, k80n, True, False, tt), 2)
    s0 = round(predict(b80, k80, True, True, tt, 0), 2)
    s1 = round(predict(b80, k80, True, True, tt, 1), 2)
    print(f"week {tt} trend-only point={p0}；情景 promo=0 -> {s0}；promo=1 -> {s1}")
    fc[tt] = {"trend_only": p0, "scenario_promo0": s0, "scenario_promo1": s1}

for h, (tt, pv) in enumerate(zip((81, 82), (0, 1)), start=1):
    trace["forecasts"].append({"id": f"o80-h{h}", "origin": 80, "target": tt,
        "features": [{"name": "promotion", "source_time": tt, "kind": "observed"}]})
for tt in (83, 84):
    trace["forecasts"].append({"id": f"o80-h{tt-80}-point", "origin": 80, "target": tt, "features": []})
    for v in (0, 1):
        trace["forecasts"].append({"id": f"o80-h{tt-80}-scn{v}", "origin": 80, "target": tt,
            "features": [{"name": "promotion", "source_time": tt, "kind": "scenario",
                          "formed_at": 80,
                          "note": f"83-84 周促销原点未知；预先固定情景 promo={v}，不使用真值"}]})

with open(os.path.join(INFO, "information-trace.json"), "w", encoding="utf-8") as f:
    json.dump(trace, f, ensure_ascii=False, indent=2)
print(f"\ntrace 已写出：{len(trace['forecasts'])} 条预测记录 -> information/information-trace.json")
print("审计命令：python3 <skill>/scripts/check_information.py --trace .../information-trace.json")
