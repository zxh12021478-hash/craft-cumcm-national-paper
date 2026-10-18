# -*- coding: utf-8 -*-
# F 题路线选择小检查（纯标准库）：
# 1) tickets 是否只是 demand 的确定性派生（泄漏风险）
# 2) 单斜率 vs 分段趋势（含促销哑变量）的样本内改善
# 3) 模拟真实预测原点的小型滚动原点比较（折内选断点），决定是否采用分段路线
import csv, statistics, os

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "inputs")
rows = []
with open(os.path.join(BASE, "demand.csv")) as f:
    for r in csv.DictReader(f):
        rows.append((int(r["week"]), float(r["demand_units"]),
                     int(r["planned_promotion"]), float(r["resolved_service_tickets"])))
n = len(rows)
t = [r[0] for r in rows]; y = [r[1] for r in rows]
promo = [r[2] for r in rows]; tick = [r[3] for r in rows]

def ols(X, yv):
    """含截距 OLS，Gauss-Jordan 消元（纯标准库）。"""
    p = len(X[0])
    Xt = [[X[i][j] for i in range(len(X))] for j in range(p)]
    XtX = [[sum(Xt[a][k]*Xt[b][k] for k in range(len(yv))) for b in range(p)] for a in range(p)]
    Xty = [sum(Xt[a][k]*yv[k] for k in range(len(yv))) for a in range(p)]
    M = [XtX[i][:] + [Xty[i]] for i in range(p)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        d = M[c][c]
        M[c] = [v/d for v in M[c]]
        for r in range(p):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][k]-f*M[c][k] for k in range(p+1)]
    return [M[i][p] for i in range(p)]

def sse_for(beta, X, yv):
    return sum((yv[i]-sum(beta[j]*X[i][j] for j in range(len(beta))))**2 for i in range(len(yv)))

print("== 1) tickets / demand 比率 ==")
ratio = [tick[i]/y[i] for i in range(n)]
print(f"ratio mean={statistics.mean(ratio):.4f} sd={statistics.stdev(ratio):.4f} "
      f"min={min(ratio):.4f} max={max(ratio):.4f}")
b = ols([[1, y[i]] for i in range(n)], tick)
res = [tick[i]-(b[0]+b[1]*y[i]) for i in range(n)]
print(f"tickets ~ {b[0]:.3f} + {b[1]:.4f}*demand, residual sd={statistics.stdev(res):.3f}")

print("\n== 2) 单斜率 vs 分段（全样本，仅诊断） ==")
X1 = [[1, t[i], promo[i]] for i in range(n)]
b1 = ols(X1, y); s1 = sse_for(b1, X1, y)
print(f"单斜率: intercept={b1[0]:.2f} slope={b1[1]:.3f} promo={b1[2]:.2f} SSE={s1:.1f}")
best = None
for k in range(35, 71):
    Xk = [[1, t[i], max(0, t[i]-k), promo[i]] for i in range(n)]
    bk = ols(Xk, y); sk = sse_for(bk, Xk, y)
    if best is None or sk < best[1]:
        best = (k, sk, bk)
k, sk, bk = best
print(f"分段最优断点 k={k}: slopes {bk[1]:.3f} -> {bk[1]+bk[2]:.3f}, promo={bk[3]:.2f}, SSE={sk:.1f}, "
      f"SSE下降={100*(s1-sk)/s1:.1f}%")

print("\n== 3) 滚动原点（origins 60..76；断点仅在折内训练数据选择） ==")
def fit_model(origin, segmented):
    idx = range(0, origin)  # 周 1..origin
    if not segmented:
        return ols([[1, t[i], promo[i]] for i in idx], [y[i] for i in idx]), None
    bestk = None
    for kk in range(35, origin-4):
        Xkk = [[1, t[i], max(0, t[i]-kk), promo[i]] for i in idx]
        bb = ols(Xkk, [y[i] for i in idx]); ss = sse_for(bb, Xkk, [y[i] for i in idx])
        if bestk is None or ss < bestk[1]:
            bestk = (kk, ss, bb)
    return bestk[2], bestk[0]

def fit_predict(origin, horizon, segmented):
    beta, kp = fit_model(origin, segmented)
    errs = []
    for h in range(1, horizon+1):
        ft = origin + h
        # promo 提前两周发布；origin 60..76、h<=4 的目标周在真实时点均已可知，使用合法
        fp = promo[ft-1]
        hinge = max(0, ft-kp) if segmented else 0.0
        pred = beta[0] + beta[1]*ft + (beta[2]*hinge if segmented else 0.0) + beta[3 if segmented else 2]*fp
        errs.append(pred - y[ft-1])
    return errs

for horizon in (1, 4):
    agg = {True: [], False: []}
    for origin in range(60, 77):
        for seg in (False, True):
            agg[seg].extend(fit_predict(origin, horizon, seg))
    for seg, name in ((False, "single"), (True, "piecewise")):
        e = agg[seg]
        mae = sum(abs(v) for v in e)/len(e)
        rmse = (sum(v*v for v in e)/len(e))**0.5
        bias = sum(e)/len(e)
        print(f"h={horizon} {name}: MAE={mae:.2f} RMSE={rmse:.2f} bias={bias:+.2f} n={len(e)}")
print("\n注意：83-84 周促销在原点 80 未知，正式预测须做情景，不得回填真值。")
