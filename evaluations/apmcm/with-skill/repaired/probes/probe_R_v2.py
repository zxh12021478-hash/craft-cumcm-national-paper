# -*- coding: utf-8 -*-
# R 修复版探针（纯标准库）。修复点：
#  (1) 单纯形步长/格点数标签由实际参数 STEP 生成（STEP=20 -> 0.05）。
#  (2) 权重区域边界用 Fraction 精确推导，不写笼统区间。
#  (3) ±5% 扰动每个样本内重新判断：预算可行性、支配关系、归一化、排序；不固定剔除 D。
#  (4) 等权仅为参照约定；采样频率一律不称概率。单位：cost 为百万元人民币（million CNY）。
import random
from fractions import Fraction as Fr

NAMES = ["A", "B", "C", "D"]
RAW = {"A": dict(cost=8, benefit=70, em=6),
       "B": dict(cost=10, benefit=80, em=7),
       "C": dict(cost=12, benefit=85, em=5),
       "D": dict(cost=11, benefit=75, em=8)}
BUDGET = 12.0
STEP = 20  # 单纯形网格分母 -> 实际步长 1/STEP

def dominance(raw):
    """在给定原始指标上返回每个方案被谁支配。"""
    out = {}
    for i, n in enumerate(NAMES):
        out[n] = [m for m in NAMES if m != n and
                  raw[m]["cost"] <= raw[n]["cost"] and
                  raw[m]["benefit"] >= raw[n]["benefit"] and
                  raw[m]["em"] <= raw[n]["em"] and
                  (raw[m]["cost"] < raw[n]["cost"] or
                   raw[m]["benefit"] > raw[n]["benefit"] or
                   raw[m]["em"] < raw[n]["em"])]
    return out

def minmax_cost(v):
    lo, hi = min(v), max(v); return [(hi-x)/(hi-lo) for x in v]
def minmax_ben(v):
    lo, hi = min(v), max(v); return [(x-lo)/(hi-lo) for x in v]

print("== Q1 名义支配筛选与预算（cost 单位：百万元人民币 / million CNY） ==")
dom = dominance(RAW)
for n in NAMES:
    print(f"{n}: cost={RAW[n]['cost']} 预算内={RAW[n]['cost']<=BUDGET} 被支配={dom[n] or '无'}")

print("\n== 权重区域精确边界（min-max 归一化，Fraction 推导） ==")
# 精确归一化
zc = {n: Fr(12-RAW[n]["cost"], 4) for n in NAMES}                       # (12-x)/4
zb = {n: Fr(RAW[n]["benefit"]-70, 15) for n in NAMES}                   # (x-70)/15
ze = {n: Fr(8-RAW[n]["em"], 3) for n in NAMES}                          # (8-x)/3
Z = {n: (zc[n], zb[n], ze[n]) for n in NAMES}
print("归一化得分 (cost, benefit, emissions):", {n: (str(Z[n][0]), str(Z[n][1]), str(Z[n][2])) for n in NAMES})

# S_i - S_j 作为 wc, we 的线性式（代入 wb=1-wc-we）
def diff_linear(i, j):
    # 返回 (常数项, wc 系数, we 系数) Fraction
    dc = Z[i][0]-Z[j][0]; db = Z[i][1]-Z[j][1]; de = Z[i][2]-Z[j][2]
    a = db                                  # wb 系数
    return (a, dc-a, de-a)                  # S_i-S_j = a0 + a1*wc + a2*we
pairs = [("C", "A"), ("C", "B"), ("B", "A"), ("B", "D"), ("A", "D"), ("C", "D")]
for i, j in pairs:
    a0, a1, a2 = diff_linear(i, j)
    print(f"S_{i}-S_{j} = {a0} {a1:+}*wc {a2:+}*we ; {i}≥{j} ⇔ {(-a1) if a1!=0 else 0}*wc {(-a2):+}*we ≤ {a0}")

print(f"\n== 单纯形枚举（STEP={STEP}，实际步长={1/STEP:.3f}，标签由参数生成） ==")
wins = {n: 0 for n in NAMES}; ties = total = 0
for a in range(STEP+1):
    for b in range(STEP+1-a):
        wc, wb = Fr(a, STEP), Fr(b, STEP); we = 1-wc-wb
        sc = {n: float(wc*Z[n][0]+wb*Z[n][1]+we*Z[n][2]) for n in NAMES}
        mx = max(sc.values()); w = [n for n in NAMES if abs(sc[n]-mx) < 1e-12]
        ties += len(w) > 1
        if len(w) == 1: wins[w[0]] += 1
        total += 1
print(f"格点总数={total}（含边界），平手格点={ties}")
for n in NAMES: print(f"  {n} 独占区域占比={wins[n]/total:.4f}")
sc_eq = {n: float((Z[n][0]+Z[n][1]+Z[n][2])/3) for n in NAMES}
print("等权参照（仅为未给权重时的约定，非真实偏好）得分：", {k: round(v, 4) for k, v in sc_eq.items()})

import math
def vec(v, ben=False):
    den = math.sqrt(sum(x*x for x in v)); return [x/den if ben else 1-x/den for x in v]
cv = vec([RAW[n]["cost"] for n in NAMES]); bv = vec([RAW[n]["benefit"] for n in NAMES], True)
ev = vec([RAW[n]["em"] for n in NAMES])
print("向量归一化等权参照：", {n: round((cv[i]+bv[i]+ev[i])/3, 4) for i, n in enumerate(NAMES)})

print("\n== ±5% 联合扰动：每样本重算预算/支配/归一化/排序（N=20000，均匀独立） ==")
random.seed(20261018)
N = 20000
winf = {n: 0 for n in NAMES}; winf_feas = {n: 0 for n in NAMES}
c_breach = 0; dom_kept = 0; dom_changed = 0; order_chg = 0
base_order = sorted(sc_eq, key=lambda k: -sc_eq[k])
for _ in range(N):
    rp = {n: dict(cost=RAW[n]["cost"]*(1+random.uniform(-.05, .05)),
                  benefit=RAW[n]["benefit"]*(1+random.uniform(-.05, .05)),
                  em=RAW[n]["em"]*(1+random.uniform(-.05, .05))) for n in NAMES}
    feas = [n for n in NAMES if rp[n]["cost"] <= BUDGET]
    if rp["C"]["cost"] > BUDGET: c_breach += 1
    d = dominance(rp)
    if d["D"] == ["B"]: dom_kept += 1
    if d["D"] != ["B"]: dom_changed += 1
    cc = [rp[n]["cost"] for n in NAMES]; bb = [rp[n]["benefit"] for n in NAMES]; ee = [rp[n]["em"] for n in NAMES]
    zc_, zb_, ze_ = minmax_cost(cc), minmax_ben(bb), minmax_cost(ee)
    sc = {NAMES[i]: (zc_[i]+zb_[i]+ze_[i])/3 for i in range(4)}
    winf[max(sc, key=sc.get)] += 1
    winf_feas[max(feas, key=lambda k: sc[k])] += 1
    if sorted(sc, key=lambda k: -sc[k]) != base_order: order_chg += 1
print("等权第一名采样频率（不限制预算，仅模拟频率非概率）：", {k: round(v/N, 4) for k, v in winf.items()})
print("等权第一名采样频率（仅预算可行者）：", {k: round(v/N, 4) for k, v in winf_feas.items()})
print(f"C 成本超 12 的采样频率={c_breach/N:.4f}；D 仍恰被 B 支配={dom_kept/N:.4f}；D 支配关系变化={dom_changed/N:.4f}")
print(f"完整排序变化采样频率={order_chg/N:.4f}")
