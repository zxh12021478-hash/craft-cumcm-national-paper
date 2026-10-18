# -*- coding: utf-8 -*-
# O 修复版探针（纯标准库，独立逐时模拟，不调用求解器）。修复点：
#  (1) 光伏利用量 u_t ∈ [0, s_t]、弃光 q_t=s_t-u_t 进入逐时平衡；不再用不一致的 s_t。
#  (2) 术语：c_t=充入侧能量（取自电网/光伏，效率前），d_t=供负荷侧（效率后）；
#      E_t=E_{t-1}+0.9*c_t-d_t/0.9；g_t+u_t+d_t=L_t+c_t。
#  (3) 保持原题不可行证书；对"显式放松后"的模型给可行例并逐时反验。
ETA = 0.9
L = [4, 7, 5]
PRICE = [1, 4, 2]
S = [0, None, 0]   # 仅 h2 有光伏 s

def simulate(g, c, d, u, s2, cap, label, tol=1e-9, quiet=False):
    """独立重算逐时平衡、储能递归、上下限与终态；返回 (ok, 明细)。"""
    s = [0, s2, 0]; E = 0.0; rows = []; ok = True
    for t in range(3):
        q = s[t] - u[t]
        # 平衡：g + u + d = L + c
        bal = abs(g[t] + u[t] + d[t] - (L[t] + c[t])) < tol
        E_new = E + ETA*c[t] - d[t]/ETA
        bounds = (-tol <= g[t] <= cap+tol and -tol <= u[t] <= s[t]+tol and q >= -tol
                  and -tol <= c[t] <= 2+tol and -tol <= d[t] <= 2+tol and -tol <= E_new <= 3+tol)
        no_both = not (c[t] > 1e-9 and d[t] > 1e-9)
        no_export = g[t] + u[t] <= L[t] + c[t] + tol
        row = dict(h=t+1, g=g[t], u=u[t], c=c[t], d=d[t], q=q, E_end=E_new,
                   bal=bal, bounds=bounds, no_both=no_both, no_export=no_export)
        rows.append(row)
        ok &= bal and bounds and no_both and no_export
        E = E_new
    ok &= abs(E) < 1e-6
    cost = sum(PRICE[t]*g[t] for t in range(3))
    if not quiet:
        print(f"-- {label}（s={s2}, cap={cap}, 成本={cost:.4f}） -> {'可行' if ok else '不可行'}")
        for r in rows:
            print(f"   h{r['h']}: g={r['g']:.4f} u={r['u']:.4f} c={r['c']:.4f} d={r['d']:.4f} "
                  f"q={r['q']:.4f} E_end={r['E_end']:.4f} 平衡={r['bal']} 界限={r['bounds']} "
                  f"无同时充放={r['no_both']} 无外送={r['no_export']}")
        print(f"   终态 E3={E:.2e}；总量恒等式 Σd=0.81Σc: {sum(d):.4f} vs {0.81*sum(c):.4f}")
    return ok, rows

print("== Q1 原题不可行证书（cap=5） ==")
print(f"总负荷={sum(L)}，电网总上限=15；电池 E0=E3=0 净供出=(0.81-1)Σc≤0；s=0 时 15<16。")
c1max = min(2, 5-L[0]); E1 = ETA*c1max
print(f"h1 最多充 {c1max}（g1≤5 且供负荷 4），E1={E1:.2f}，h2 最多供 {ETA*E1:.2f}")
s_star = L[1]-5-ETA*E1
print(f"保证可行最小光伏 s*=7-5-{ETA*E1:.2f}={s_star:.3f} kWh")

print("\n== R1 放松：主办方保证 s≥1.19，cap=5；日前固定 g=[5,5,5], c1=1，h2 追索 ==")
fails = []
for k in range(119, 401):
    sv = k/100
    g, c, d, u = [5, 5, 5], [1, 0, 0], [0, 0.81, 0], [0, 1.19, 0]
    ok, _ = simulate(g, c, d, u, sv, 5, f"R1 网格点 s={sv}", quiet=True)
    if not ok: fails.append(sv)
print("（网格扫描静默，仅打印端点明细）")
simulate([5,5,5],[1,0,0],[0,0.81,0],[0,1.19,0], 1.19, 5, "R1 端点 s=1.19")
simulate([5,5,5],[1,0,0],[0,0.81,0],[0,1.19,0], 4.0, 5, "R1 端点 s=4.00（弃光 q=2.81）")
print(f"R1 在 s∈[1.19,4.00] 步长0.01 共 {400-119+1} 点全部可行: {len(fails)==0}")
print("负对照（应失败）：s=1.0 < s* 时 h2 平衡 5+1.0+0.81=6.81<7")
ok, _ = simulate([5,5,5],[1,0,0],[0,0.81,0],[0,1.0,0], 1.0, 5, "负对照 s=1.0")
print(f"负对照判定不可行: {not ok}")

print("\n== R2 放松：cap=6、s=0 的短可行例（h1 多充恰好满足 h2 缺口） ==")
c1 = 1/0.81                 # 使 0.81*c1=1.0
g1 = L[0] + c1
simulate([g1, 6, 5], [c1, 0, 0], [0, 1.0, 0], [0, 0, 0], 0, 6, "R2 例 s=0")
print(f"（g1={g1:.4f}≤6，c1={c1:.4f}≤2；g3=5 日前固定，无需日内调整）")

print("\n== 决策时点（防泄漏） ==")
print("日前（here-and-now，不依赖 s）：g1,g2,g3,c1；实时（h2 见 s 后）：u2,q2,d2（R1 中 d2=0.81 固定）。")
