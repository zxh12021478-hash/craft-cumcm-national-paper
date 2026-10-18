#!/usr/bin/env python3
# O 题小检查：用 LP 核验 s=0 不可行证书、最小保证 s、松弛需求、各 s 下的最小成本 recourse
# 变量: g1,g2,g3(电网), c1,c2(充电量,电池侧前), d2,d3(放电量,SOC侧), q2(弃负荷)
# 约定: 充电 c -> SOC+0.9c; 放电 d -> 负荷+0.9d; 同时段不充不放用约束保证
import numpy as np
from scipy.optimize import linprog

# 变量顺序: g1,g2,g3,c1,c2,d2,d3,q2
LB = np.array([0, 0, 0, 0, 0, 0, 0, 0.0])
UB = np.array([5, 5, 5, 2, 2, 2, 2, 7.0])
eta = 0.9

def solve(s, g2_max=5.0, allow_shed=False, min_obj="shed", cap_g2_var=False):
    """返回 (状态, 变量, 目标值)。cap_g2_var=True 时 g2 上界放到 7 并最小化 g2。"""
    ub = UB.copy()
    ub[1] = 7.0 if cap_g2_var else g2_max
    if not allow_shed:
        ub[7] = 0.0
    # 等式: 3小时平衡 + 终端SOC=0
    Aeq = np.array([
        [1, 0, 0, -1, 0, 0, 0, 0],          # h1: g1 - c1 = 4
        [0, 1, 0, 0, -1, eta, 0, 1],        # h2: g2 - c2 + .9d2 + q2 = 7-s
        [0, 0, 1, 0, 0, 0, eta, 0],         # h3: g3 + .9d3 = 5
        [0, 0, 0, eta, eta, -1, -1, 0],     # 终端: .9c1+.9c2-d2-d3=0
    ], dtype=float)
    beq = np.array([4.0, 7.0 - s, 5.0, 0.0])
    # 不等式: E2>=0; E2<=3; d2<=E1(放电前SOC)
    Aub = np.array([
        [0, 0, 0, -eta, -eta, 1, 0, 0],     # d2 - .9c1 - .9c2 <= 0
        [0, 0, 0, eta, eta, -1, 0, 0],      # .9c1+.9c2-d2 <= 3
        [0, 0, 0, -eta, 0, 1, 0, 0],        # d2 <= .9c1
    ], dtype=float)
    bub = np.array([0.0, 3.0, 0.0])
    if min_obj == "shed":
        c = np.array([0, 0, 0, 0, 0, 0, 0, 1.0])  # 最小弃负荷
        if not allow_shed:
            ub[7] = 0.0
    elif min_obj == "cost":
        c = np.array([1.0, 4.0, 2.0, 0, 0, 0, 0, 1e4])
    elif min_obj == "g2":
        c = np.array([0, 1.0, 0, 0, 0, 0, 0, 0])
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                  bounds=list(zip(LB, ub)), method="highs")
    return res

print("== Q1 总量证书（s=0 最坏情形） ==")
print(f"三小时负荷合计={4+7+5} kWh；电网三小时上限合计={5*3} kWh；电池往返效率=.9*.9={eta*eta:.2f}<1，不能造能")
r0 = solve(0.0, allow_shed=False)
print(f"s=0 且不允许弃负荷: LP 可行性 = {r0.status == 0}（status {r0.status}, 0=最优可行）")

r0s = solve(0.0, allow_shed=True, min_obj="shed")
print(f"s=0 允许弃负荷并最小化: 最小弃负荷 q2 = {r0s.x[7]:.4f} kWh（第2小时）")

r0c = solve(0.0, allow_shed=False, min_obj="g2", cap_g2_var=True)
print(f"s=0 改为放宽第2小时电网上限: 最小 g2 = {r0c.x[1]:.4f} kWh（即上限需≥约6.19，原5）")

# 求保证可行的最小 s（把 s 加为变量最小化：直接二分）
def feasible(s):
    r = solve(s, allow_shed=False)
    return r.status == 0

lo, hi = 0.0, 4.0
for _ in range(40):
    mid = (lo + hi) / 2
    if feasible(mid):
        hi = mid
    else:
        lo = mid
print(f"\n二分求全局(oracle式)最小保证光照: s_min = {hi:.4f} kWh")
print("解析核对: h1 最多充 1 kWh(g1<=5,负荷4) -> 储存0.9 -> h2放电0.81; h2 缺口 2-0.81=1.19")

print("\n== Q2 各 s 下最小成本 recourse（价格 1,4,2；仅 s>=s_min 可行） ==")
for s in [0.0, 1.0, 1.19, 2.0, 3.0, 4.0]:
    r = solve(s, allow_shed=True, min_obj="cost")
    if r is None or r.status != 0:
        print(f"s={s}: 不可行")
        continue
    g1, g2, g3, c1, c2, d2, d3, q2 = r.x
    costv = g1*1 + g2*4 + g3*2
    print(f"s={s:>4}: 成本={costv:6.2f}  g=({g1:.2f},{g2:.2f},{g3:.2f}) "
          f"c1={c1:.2f} c2={c2:.2f} d2={d2:.2f} d3={d3:.2f} 弃负荷={q2:.3f}")

print("\n== 物理一致性自检（对 s=1.19..4 的解逐小时重算平衡残差） ==")
for s in [1.19, 2.0, 4.0]:
    r = solve(s, allow_shed=False, min_obj="cost")
    g1, g2, g3, c1, c2, d2, d3, q2 = r.x
    e1 = eta*c1
    e2 = e1 + eta*c2 - d2
    e3 = e2 - d3
    bal1 = g1 - c1 - 4
    bal2 = g2 + s + eta*d2 - c2 - 7
    bal3 = g3 + eta*d3 - 5
    print(f"s={s}: 残差=({bal1:+.2e},{bal2:+.2e},{bal3:+.2e}), SOC=({e1:.3f},{e2:.3f},{e3:.3f}), "
          f"限界 g<=5={all(v<=5+1e-6 for v in (g1,g2,g3))}, c/d<=2={max(c1,c2,d2,d3)<=2+1e-6}")
