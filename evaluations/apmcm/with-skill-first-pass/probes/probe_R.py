# -*- coding: utf-8 -*-
# R 题路线选择小检查（纯标准库，确定性枚举）：
# 1) 三维支配筛选（cost/emissions 越小越好，benefit 越大越好）+ 预算 12
# 2) min-max 归一化下权重单纯形划分（谁在什么权重区胜出），等权基准
# 3) ±5% 联合测量扰动 + 重新归一化的胜率/排序反转（蒙特卡洛，小规模探针）
# 完整的扰动规模、归一化对照与后悔值分析由 Modex 执行。
import itertools, random

A = dict(cost=8, benefit=70, em=6)
B = dict(cost=8+2, benefit=80, em=7)
C = dict(cost=12, benefit=85, em=5)
D = dict(cost=11, benefit=75, em=8)
des = {"A": A, "B": B, "C": C, "D": D}
BUDGET = 12

print("== 1) 支配筛选与预算 ==")
for name, x in des.items():
    feas = x["cost"] <= BUDGET
    dom = []
    for oname, o in des.items():
        if oname == name: continue
        if (o["cost"] <= x["cost"] and o["benefit"] >= x["benefit"] and o["em"] <= x["em"]
                and (o["cost"] < x["cost"] or o["benefit"] > x["benefit"] or o["em"] < x["em"])):
            dom.append(oname)
    print(f"{name}: feasible={feas}, dominated_by={dom or '无'}")

def minmax(vals):
    lo, hi = min(vals), max(vals)
    return [(hi-v)/(hi-lo) for v in vals]  # 成本型：越小越接近1

def vecnorm(vals, benefit=False):
    # 向量归一化：效益型 x/sqrt(sum x^2)；成本型取 1 - 该值
    import math
    den = math.sqrt(sum(v*v for v in vals))
    z = [v/den for v in vals]
    return z if benefit else [1-zz for zz in z]

names = list(des)
costs = [des[k]["cost"] for k in names]
bens  = [des[k]["benefit"] for k in names]
ems   = [des[k]["em"] for k in names]

print("\n== 2) 权重单纯形（min-max 归一化，step=0.02 枚举） ==")
Zc, Zb, Ze = minmax(costs), minmax([-b for b in bens]) if False else None, None
# benefit 是效益型
def minmax_benefit(vals):
    lo, hi = min(vals), max(vals)
    return [(v-lo)/(hi-lo) for v in vals]
Zc = minmax(costs)                 # 成本得分
Zb = minmax_benefit(bens)          # 效益得分
Ze = minmax(ems)                   # 排放得分
print("归一化得分 (cost, benefit, emissions):")
for i, nm in enumerate(names):
    print(f"  {nm}: {Zc[i]:.3f}, {Zb[i]:.3f}, {Ze[i]:.3f}")

step = 20
wins = {k: 0 for k in names}; ties = 0; total = 0
for a in range(0, step+1):
    for b in range(0, step-a+1):
        wc, wb = a/step, b/step
        we = 1-wc-wb
        sc = {nm: wc*Zc[i]+wb*Zb[i]+we*Ze[i] for i, nm in enumerate(names)}
        mx = max(sc.values())
        win = [k for k in names if abs(sc[k]-mx) < 1e-12]
        if len(win) > 1: ties += 1
        else: wins[win[0]] += 1
        total += 1
print(f"单纯形格点总数={total}, 平手格点={ties}")
for k in names:
    print(f"  {k} 独占胜率={wins[k]/total:.3f}")
eq = 1/3
sc_eq = {nm: eq*(Zc[i]+Zb[i]+Ze[i]) for i, nm in enumerate(names)}
print("等权得分:", {k: round(v, 4) for k, v in sc_eq.items()})

# 半空间边界（min-max 下）：符号化给出，供 Modex 解析复核
print("\n关键权重边界（min-max 线性得分，令权重为 wc,wb,we，和=1）:")
print("  B 支配 D（与权重无关）；C 与 A/B 的分界可由得分差半空间解析给出，交 Modex 复算")

print("\n== 2b) 向量归一化等权对照 ==")
Vc = vecnorm(costs); Vb = vecnorm(bens, benefit=True); Ve = vecnorm(ems)
sc_v = {nm: eq*(Vc[i]+Vb[i]+Ve[i]) for i, nm in enumerate(names)}
print("向量归一化等权得分:", {k: round(v, 4) for k, v in sc_v.items()})

print("\n== 3) ±5% 联合扰动（等权；min-max；2000 次；含归一化随扰动重算） ==")
random.seed(20261018)
def scores_for(cv, bv, ev):
    zc = minmax(cv); zb = minmax_benefit(bv); ze = minmax(ev)
    return {nm: eq*(zc[i]+zb[i]+ze[i]) for i, nm in enumerate(names)}
win_count = {k: 0 for k in names}; rank_reversal = 0
base_order = [k for k, _ in sorted(sc_eq.items(), key=lambda kv: -kv[1])]
N = 2000
for _ in range(N):
    cv = [des[k]["cost"]*(1+random.uniform(-0.05, 0.05)) for k in names]
    bv = [des[k]["benefit"]*(1+random.uniform(-0.05, 0.05)) for k in names]
    ev = [des[k]["em"]*(1+random.uniform(-0.05, 0.05)) for k in names]
    sc = scores_for(cv, bv, ev)
    win = max(sc, key=sc.get)
    win_count[win] += 1
    order = [k for k, _ in sorted(sc.items(), key=lambda kv: -kv[1])]
    if order != base_order: rank_reversal += 1
print("等权下扰动胜率:", {k: round(v/N, 3) for k, v in win_count.items()})
print(f"完整排序发生变化比例={rank_reversal/N:.3f}")
print("（探针：仅等权+均匀独立扰动；权重扫描×扰动联合、最坏角点、后悔值交 Modex）")
