#!/usr/bin/env python3
# F 题小检查：数据趋势、促销效应、工单可用性、滚动原点回测（模拟真实预测原点）
# 仅用 numpy，输出到 stdout，由调用方保存为 check_F_output.txt
import csv, math
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(BASE / "inputs" / "demand.csv")))
t = np.array([int(r["week"]) for r in rows], dtype=float)
y = np.array([float(r["demand_units"]) for r in rows])
p = np.array([int(r["planned_promotion"]) for r in rows], dtype=float)
z = np.array([float(r["resolved_service_tickets"]) for r in rows])

print("== 基本统计 ==")
print(f"n={len(y)}, 周1-20均值={y[:20].mean():.2f}, 周21-40均值={y[20:40].mean():.2f}, "
      f"周41-60均值={y[40:60].mean():.2f}, 周61-80均值={y[60:].mean():.2f}")
print(f"最近12周均值={y[-12:].mean():.2f}, 周80={y[-1]:.2f}")

# 整体线性趋势
X = np.column_stack([np.ones_like(t), t, p])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
resid = y - X @ beta
print("\n== 全局线性模型 y=a+b*t+c*promo ==")
print(f"a={beta[0]:.3f}, b={beta[1]:.4f}/周, 促销系数c={beta[2]:.3f}, 残差SD={resid.std(ddof=3):.2f}")
ac1 = np.corrcoef(resid[:-1], resid[1:])[0, 1]
print(f"残差滞后1阶自相关={ac1:.3f}")

# 工单：同期关系与滞后可用性
ratio = z / y
print("\n== 工单 ==")
print(f"z/y 同期比: 均值={ratio.mean():.4f}, 范围={ratio.min():.4f}~{ratio.max():.4f}")
# 同期 z_t 对 y_t 的线性拟合
b0, b1 = np.polyfit(y, z, 1)
print(f"z_t ≈ {b1:.3f} + {b0:.4f}*y_t, 相关={np.corrcoef(y,z)[0,1]:.4f}")
# 原点80时 z 只到79；检验 z_{t-1} 对 y_t 增量信息（在趋势+促销之上）
Xlag = np.column_stack([np.ones_like(t[1:]), t[1:], p[1:], z[:-1]])
bl, *_ = np.linalg.lstsq(Xlag, y[1:], rcond=None)
rl = y[1:] - Xlag @ bl
print(f"加入 z_{{t-1}} 后残差SD={rl.std(ddof=4):.2f}（对比 {resid.std(ddof=3):.2f}），z滞后系数={bl[3]:.4f}")

# 分段线性模型（带一个折点）
def piecewise(k, tt, pp):
    return np.column_stack([np.ones_like(tt), tt, np.maximum(tt - k, 0), pp])

# 内层面板选折点：每个外原点用内层滚动选 knot，避免未来信息
def rolling_eval(piecewise_flag, origins=range(44, 77)):
    errs = {h: [] for h in range(1, 5)}
    p_marginal = p.mean()  # 83-84 促销未知时用边际频率
    for o in origins:
        tt, yy, pp = t[:o], y[:o], p[:o]
        if piecewise_flag:
            # 内层选折点（候选 25..o-10）
            best = None
            for k in range(25, o - 9):
                inner = []
                for io in range(max(24, k + 5), o - 3):
                    Xi = piecewise(k, t[:io], p[:io])
                    bi, *_ = np.linalg.lstsq(Xi, y[:io], rcond=None)
                    for h in range(1, 4):
                        pf = p_marginal if h >= 3 else p[io + h - 1]  # 促销提前2周已知
                        Xf = np.array([1, t[io + h - 1], max(t[io + h - 1] - k, 0), pf])
                        inner.append((y[io + h - 1] - Xf @ bi) ** 2)
                m = np.mean(inner)
                if best is None or m < best[0]:
                    best = (m, k)
            k = best[1]
            Xo = piecewise(k, tt, pp)
        else:
            Xo = np.column_stack([np.ones_like(tt), tt, pp])
        bo, *_ = np.linalg.lstsq(Xo, yy, rcond=None)
        for h in range(1, 5):
            tf = t[o + h - 1]
            pf = p_marginal if h >= 3 else p[o + h - 1]
            if piecewise_flag:
                Xf = np.array([1, tf, max(tf - k, 0), pf])
            else:
                Xf = np.array([1, tf, pf])
            errs[h].append((y[o + h - 1] - Xf @ bo) ** 2)
    return {h: math.sqrt(np.mean(v)) for h, v in errs.items()}

print("\n== 滚动原点回测：外原点=44..79（共36个），预测1~4周 ==")
print("协议：原点o仅用 demand<=o；促销仅提前2周已知（h>=3用边际频率替代）；每原点重拟合")
base_rmse = rolling_eval(False)
pw_rmse = rolling_eval(True)
print(f"基线(线性趋势+促销) RMSE: " + ", ".join(f"h{h}={v:.2f}" for h, v in base_rmse.items()))
print(f"分段线性(折点内层选) RMSE: " + ", ".join(f"h{h}={v:.2f}" for h, v in pw_rmse.items()))

# 用全样本拟合的分段模型，给出折点位置（仅描述用）
best = None
for k in range(30, 70):
    Xk = piecewise(k, t, p)
    bk, *_ = np.linalg.lstsq(Xk, y, rcond=None)
    sse = ((y - Xk @ bk) ** 2).sum()
    if best is None or sse < best[0]:
        best = (sse, k, bk)
sse, k, bk = best
print(f"\n全样本分段拟合最优折点≈周{k}，前段斜率={bk[1]:.3f}/周，后段斜率={bk[1]+bk[2]:.3f}/周，"
      f"促销系数={bk[3]:.2f}，残差SD={math.sqrt(sse/(len(y)-4)):.2f}")

# 81-84 预测（分段模型，83/84 促销两种情形）
print("\n== 原点80 点预测（分段模型，仅作流程演示，不构成精度承诺） ==")
future_promo = {81: 0, 82: 1}  # 来自 metadata.json；83/84 在原点80未知
for w in range(81, 85):
    tf = float(w)
    if w <= 82:
        pf = future_promo[w]
        v = np.array([1, tf, max(tf - k, 0), pf]) @ bk
        print(f"周{w} 促销={pf:.0f}: 点预测={v:.1f}")
    else:
        v0 = np.array([1, tf, max(tf - k, 0), 0.0]) @ bk
        v1 = np.array([1, tf, max(tf - k, 0), 1.0]) @ bk
        print(f"周{w} 促销未知: 无促销={v0:.1f}, 有促销={v1:.1f}, 边际概率={p.mean():.3f}")
print(f"历史促销频率={p.mean():.3f}")
