# F 例 note

## 关键主张定位
- 筛选规则（served/100 ≥ 0.90 且 max_hours ≤ 6，再取最小成本）：paper.md「Model and method」；results.json `base.feasible`、`stress.feasible`；solve.py 第 8–10 行。
- Q1 选 B：paper.md「Base results (Q1)」；results.json `base.chosen`（B, 210, 95, 5.0h）。
- 对 A 节省 12.5%：paper.md「Base results (Q1)」末；results.json `base.saving_vs_A = 0.125`；solve.py 第 11 行。
- C 因 7.0h 超时被排除、E 满足 6.0h 边界：paper.md「Base results (Q1)」表。
- Q2 仅 D 可行：paper.md「Stress results (Q2)」；results.json `stress.feasible = ["D"]`、`stress.chosen`（255, 94, 5.7h）；B 服务 84% 不达标、E 6.5h 超时均在该节。
- 场景化推荐与边界：paper.md「Conclusion and limits」；results.json `scope`。

## 删掉了什么
- 原 Summary 逐行罗列两批共 10 条政策的完整数据（与正文两张表重复），只保留起决定作用的事实：C 超时被排除、B 为基批最优、12.5% 对比、D 为压力批唯一可行及 B/E 的失败原因。
- 合并了口径说明（成本/服务分母/时间口径）为一句。

## 未验证项
- 合成表并非经过验证的模拟器；未验证任何控制器实现或现场表现。
- 两批之间无分布联系；未对未来批次、全部可能策略、置信区间或可靠性概率作任何断言（原摘要已声明，新摘要保留）。
- 未引入正文外的新结果或派生数字。
