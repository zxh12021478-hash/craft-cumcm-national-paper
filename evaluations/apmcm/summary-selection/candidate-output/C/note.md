# C 案 note

## 关键主张定位
- 模块参数（容量 A4/B3/C5 units/day，成本 7/5/10 CNY）：paper.md「Model and baseline」；solve.py L7–L8。
- 穷举 2³=8 个子集、恰好 4 个可行（A+B=12、B+C=15、A+C=17、A+B+C=22）：paper.md「Exact solution and proof」；results.json `candidates` 八行（含不可行行）；solve.py L10–L17。
- Q1 唯一最优 A+B，CNY 12，正常供给 7：results.json `optimal_designs`；solve.py 取可行集最小成本。
- 较定义参考 B+C（CNY 15）降 (15−12)/15=20%：paper.md 证明段；results.json `reference_cost_cny=15`、`cost_reduction=0.2`；solve.py L18。
- Q2：失 A 余 B=3、失 B 余 A=4，均 ≥3：results.json `optimal_designs.single_failure_supply={A:3,B:4}`；paper.md 证明段。
- solve.py 复跑结果与 results.json 逐行一致（整数算术，穷举证明而非求解器状态）。

## 删掉了什么
- 完整 8 行候选 ledger（含空集与单模块不可行行）——保留在 results.json 与正文证明段，摘要只保留四个可行设计的成本作为唯一性证据。
- 0/1 整数规划的目标函数与约束系数写法；参考设计 B+C 的故障后供给（3/5）明细；「无需 held-out 数据」「无随机搜索/学习参数」等审查性说明。
- 正文 Task 段对原题的重复照抄；未新增任何正文未报告的数字。

## 未验证项 / 边界
- 结论仅对题设加性容量、不可分割模块与给定单故障偶发集精确成立；属数学穷举证明。
- 无硬件测量、无容量物理验证、无故障概率模型；不覆盖未指定的多重故障或其他场景，不外推为可靠性结论。
