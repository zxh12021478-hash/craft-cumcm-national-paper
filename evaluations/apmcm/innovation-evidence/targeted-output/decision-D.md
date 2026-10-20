# decision-D：算法失败，要不要改题 / 下一步交接

## 结论（无需再搜索）

- **不改题，不放松需求 6**（`x+y≥6` 不得改成 `≥5`）。放松硬约束去迁就失败的求解器，等于换题，答案对原题无效。
- **本题可信答案已确定**：`(x,y)=(2,4)`，最小成本 `C=2x+y=8`，且为唯一最优解。基础方法结果正确，直接冻结。
- **停止搜索**。60 次无可行解、最后输出 `(1,1)` 的复杂优化器是**失败候选，不是原问题不可行的证据**（失败求解器 ≠ 不可行性证书）；用户明确不研究算法性能，不做算法对比实验。

## 决定性证据（已执行，廉价试算，输出保留于下）

解析证书（连续 LP，直接成立）：

1. 由 `y≤4` 与 `x+y≥6` 得 `x≥2`；
2. `C=2x+y=(x+y)+x≥6+2=8`；
3. `(2,4)` 满足 `x+y=6≥6`、`0≤2≤4`、`0≤4≤4`，且 `C=8`，达到下界 ⇒ 全局最优；等号要求 `x+y=6` 且 `x=2`，故唯一。
4. 复杂优化器输出 `(1,1)`：`1+1=2<6`，不可行，必须拒绝。

本地独立复核输出：

```
analytic: (2,4) feasible = True  C = 8
(1,1) feasible = False  C = 3
scipy linprog: success = True  x = [2. 4.]  fun = 8.0
```

解析界与独立 LP 求解器一致，证据闭环。

## 交给 Modex 的下一步（可直接执行）

> Freeze the answer to the original LP: minimizer (x,y)=(2,4), optimal cost C=8. In the manuscript, (1) state the full model exactly as given (min C=2x+y s.t. x+y≥6, 0≤x≤4, 0≤y≤4), with no relaxation of any requirement; (2) prove optimality with the analytic lower bound y≤4 ⇒ x≥2 ⇒ C=(x+y)+x≥8, attained at (2,4), and report the independent LP solver check (solver, status, convergence tolerance) as reproducibility; (3) independently substitute (2,4) into every constraint and show the reported (1,1) is infeasible (1+1=2<6); (4) record the failed optimizer (60 runs, no feasible solution, final infeasible output (1,1)) only as an implementation diagnostic / counterexample — it must not be cited as evidence of problem infeasibility, and no algorithm-performance study is required. Acceptance checks: all constraints independently residual-checked, lower-bound argument present, units and objective caliber stated, every requirement answered. Return traceable equation/result/claim locators. Do not invent values or runs; do not change any requirement to make a solver succeed.

## 停止条件

- 答案已 `verified`，不再追加搜索、不换算法、不跑锦标赛。
- 唯一可重启路线的条件：拿到与上述不同的**原题文本**（如约束/目标被证明转述错误）；否则本题关闭。
