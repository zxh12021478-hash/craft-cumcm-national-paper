# C 例 note

## 关键主张定位
- 模块参数（A: 4/7，B: 3/5，C: 5/10）与约束（正常 ≥7、单失效后 ≥3）：paper.md「Model and baseline」；solve.py 第 7–8 行。
- Q1 唯一最优 A+B，成本 12：paper.md「Exact solution and proof」；results.json `optimal_designs`（installed [A,B], cost 12, normal 7）。
- 四个可行设计及成本（A+B 12、B+C 15、A+C 17、A+B+C 22）：同节；results.json 全部 8 行 `candidates` 中 `feasible = true` 的四条。
- Q2 单失效剩余供应：A 失效→3（仅 B）、B 失效→4（仅 A）：同节；results.json A+B 行 `single_failure_supply = {"A":3,"B":4}`。
- 对定义参考 B+C（15）降低 20%：paper.md「Model and baseline」「Exact solution and proof」；results.json `reference`、`reference_cost_cny`、`cost_reduction = 0.2`；solve.py 第 18 行。
- 边界：paper.md「Conclusion and limits」；results.json `scope`。

## 删掉了什么
- 原 Summary 未逐行展开，已较简洁；重构时去掉与正文重复的参照设计细节（B+C 的 8/3/5 数据），仅保留其成本作为对比基准。
- 不重述「整数枚举、无随机搜索」等方法细节，只保留「枚举 8 个子集、四个可行」这一支撑结论的关键事实。

## 未验证项
- 精确枚举结果仅在给定的容量可加、模块不可分割模型与既定单失效条件集下成立；无硬件实测、失效概率、多模块同时失效或其他未列明工况的结论。
- 参考设计 B+C 仅为任务/正文显式定义的比较对象，未声称其为最优启发式。
- 未引入正文外的新结果或派生数字。
