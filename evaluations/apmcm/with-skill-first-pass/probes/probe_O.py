# -*- coding: utf-8 -*-
# O 题路线选择小检查（纯标准库，解析界/逐时平衡验证，不调用求解器）：
# Q1: 对所有 s in [0,4] 保证可行？ -> s=0 总量证书 + 逐时瓶颈
# Q2: 两阶段（日前 g_t 承诺、s 显现后电池追索）所需的最小 s 保证 / 容量放松
# Q3: 物理一致性检查清单的数值依据
ETA = 0.9
load = [4, 7, 5]
price = [1, 4, 2]
CAP = 5
BAT = 3.0
CLIM = 2.0

print("== Q1 不可行证书（最坏 s=0） ==")
total_load = sum(load)
max_grid = CAP * 3
print(f"总负荷={total_load}, 电网总上限={max_grid}")
# 电池 E0=E3=0：净供出 = (eta^2-1)*总充电 <= 0，电池不能创造能量
print(f"电池净能量贡献 = (eta^2-1)*总充电 <= 0；eta^2={ETA**2:.3f}")
print(f"s=0 时最大可用={max_grid} < {total_load} => 对所有 s 保证可行：False")

print("\n== 逐时瓶颈（cap=5，s 只在 h2） ==")
# h1: g1<=5，负荷 4，最多 1 单位充电；E1=0.9*1；h2 最多供出 0.9*E1
c1 = min(CLIM, CAP - load[0])
E1 = ETA * c1
deliver_h2 = ETA * E1
need_s = load[1] - CAP - deliver_h2
print(f"h1 最大充电={c1}（受 g1<=5 与负荷4 夹逼），E1={E1:.2f}, h2 最多可供={deliver_h2:.2f}")
print(f"h2 平衡 5 + s + {deliver_h2:.2f} >= 7 => 最小保证 s = {need_s:.3f} kWh")
print("h3: g3=5 恰好覆盖负荷5；终态 E3=0 要求充入全部放完")

print("\n== 放松方案对照 ==")
for cap in (5, 6):
    c = min(CLIM, cap - load[0])
    E = ETA * c
    d = ETA * E
    print(f"cap={cap}: h1 充电={c}, h2 电池可供={d:.2f}, h2 合计={cap+d:.2f}>=7: {cap+d>=load[1]}, "
          f"总电网={cap*3}>={total_load}: {cap*3>=total_load}")

print("\n== Q3 守恒恒等式（求解器结果必须独立重算通过） ==")
print("约定 E_t=E_{t-1}+0.9*c_t-d_t/0.9（c 为充入侧、d 为供负荷侧）")
print("逐时平衡：g_t + s_t + d_t = load_t + c_t；0<=E_t<=3；E0=E3=0")
print("总量恒等式：sum d = 0.81 sum c；c_t,d_t<=2；g_t<=5；无外送、无弃负荷")
print("LP 松弛需检查同时充放（亏损套利）与 s 未现即回填日前决策（完美信息泄漏）")

print("\n== 价格套利结构（供两阶段目标参考） ==")
print("price=[1,4,2]：h1 充电、h2 放电方向正确；但可行性证书先于成本优化")
