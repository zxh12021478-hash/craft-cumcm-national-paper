#!/usr/bin/env python3
# R 题小检查：占优剔除、权重单纯形上的胜者区域、等权重结果、±5% 蒙特卡洛稳定性
# 仅用 numpy 标准库，输出 stdout
import itertools
import numpy as np

names = ["A", "B", "C", "D"]
cost = np.array([8, 10, 12, 11], dtype=float)
benefit = np.array([70, 80, 85, 75], dtype=float)
emissions = np.array([6, 7, 5, 8], dtype=float)
budget = 12

print("== Q1 预算 ==")
print("成本:", dict(zip(names, cost.astype(int))), f"预算={budget} -> 全部满足（A8 B10 C12 D11）")

print("\n== Q1 原始值上的逐对占优（成本/排放越低越好，效益越高越好） ==")
for i, j in itertools.combinations(range(4), 2):
    better = int(cost[i] < cost[j]) + int(benefit[i] > benefit[j]) + int(emissions[i] < emissions[j])
    worse = int(cost[i] > cost[j]) + int(benefit[i] < benefit[j]) + int(emissions[i] > emissions[j])
    if better == 3:
        print(f"{names[i]} 严格占优 {names[j]}")
    elif worse == 3:
        print(f"{names[j]} 严格占优 {names[i]}")
    else:
        print(f"{names[i]} vs {names[j]}: 互有优劣，不占优")

# 极差归一化（成本、排放为成本型）
def norm(c, b, e):
    cs = (c.max() - c) / (c.max() - c.min())
    bs = (b - b.min()) / (b.max() - b.min())
    es = (e.max() - e) / (e.max() - e.min())
    return np.column_stack([cs, bs, es])

S = norm(cost, benefit, emissions)
print("\n== 归一化得分矩阵（列：成本权/效益权/排放权） ==")
for n_, row in zip(names, S):
    print(f"{n_}: {row[0]:.4f}, {row[1]:.4f}, {row[2]:.4f}")

# 权重单纯形网格枚举
grid = np.arange(0, 1.0001, 0.02)
wins = {n_: 0 for n_ in names}
total = 0
margin_samples = []
for wc in grid:
    for we in grid:
        wb = 1 - wc - we
        if wb < -1e-9:
            continue
        w = np.array([wc, wb, we])
        sc = S @ w
        win = int(np.argmax(sc))
        wins[names[win]] += 1
        total += 1
        margin_samples.append((wc, wb, we, sc.copy()))
print(f"\n== 权重单纯形枚举（步长0.02，共{total}点）的胜者计数 ==")
for n_ in names:
    print(f"{n_}: {wins[n_]} ({wins[n_]/total:.1%})")

# 顶点与等权重
print("\n== 单纯形顶点与等权重 ==")
for label, w in [("纯成本权", (1, 0, 0)), ("纯效益权", (0, 1, 0)), ("纯排放权", (0, 0, 1)),
                 ("等权重", (1/3, 1/3, 1/3))]:
    sc = S @ np.array(w)
    print(f"{label}: " + ", ".join(f"{n_}={v:.3f}" for n_, v in zip(names, sc)) +
          f" -> 胜者 {names[int(np.argmax(sc))]}")

# 成对反转条件（符号由归一化矩阵解析得到，这里数值化输出临界线采样）
print("\n== 关键成对反转条件（w_c,w_b,w_e，和为1） ==")
# A=C 时: 2 wc + 2/3 we = 1；B=C 时: 5/6 wc - 1/3 we = 1/3
print("C 胜 A 条件: 2*w_c + (2/3)*w_e <= 1")
print("C 胜 B 条件: (5/6)*w_c - (1/3)*w_e <= 1/3")
for wc in [0.2, 0.333, 0.4, 0.5, 0.6]:
    for we in [0.0, 0.2, 0.4]:
        wb = 1 - wc - we
        if wb < 0:
            continue
        sc = S @ np.array([wc, wb, we])
        print(f"  w=({wc:.2f},{wb:.2f},{we:.2f}) -> 胜者{names[int(np.argmax(sc))]}, 得分" +
              " ".join(f"{v:.3f}" for v in sc))

# Q3 ±5% 蒙特卡洛：属性独立均匀扰动，归一化随扰动重算
rng = np.random.default_rng(20261018)
N = 20000
weight_sets = [("等权", np.array([1/3, 1/3, 1/3])),
               ("单纯形随机", None)]
for label, wfix in weight_sets:
    rank_count = {n_: 0 for n_ in names}
    winner_d = 0
    top1 = {n_: 0 for n_ in names}
    for it in range(N):
        c2 = cost * (1 + rng.uniform(-0.05, 0.05, 4))
        b2 = benefit * (1 + rng.uniform(-0.05, 0.05, 4))
        e2 = emissions * (1 + rng.uniform(-0.05, 0.05, 4))
        S2 = norm(c2, b2, e2)
        if wfix is not None:
            w = wfix
        else:
            w = rng.dirichlet([1, 1, 1])
        sc = S2 @ w
        order = np.argsort(-sc)
        if names[int(order[0])] == "D":
            winner_d += 1
        top1[names[int(order[0])]] += 1
        if list(np.array(names)[order]) == ["C", "B", "A", "D"]:
            rank_count["C"] += 1  # 占位计数：完整序
    print(f"\n== Q3 ±5% 扰动 {N} 次（{label}） ==")
    print("第一名分布:", {k: f"{v/N:.1%}" for k, v in top1.items()})
    print("D 拿第一的比例:", f"{winner_d/N:.2%}")

# 等权重下 C 与 B、A 的名义分差（决定5%扰动是否足以翻转）
w = np.array([1/3, 1/3, 1/3])
sc = S @ w
print("\n== 等权重名义分差（对照±5%扰动幅度） ==")
print(f"C-B={sc[2]-sc[1]:.4f}, C-A={sc[2]-sc[0]:.4f}, B-A={sc[1]-sc[0]:.4f}, B-D={sc[1]-sc[3]:.4f}")
