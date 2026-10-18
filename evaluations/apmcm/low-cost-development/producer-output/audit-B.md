# B 摘要重构审查记录（开发测试，非正式比赛）

## 范围与依据
- 输入：完整短论文 `paper-B.md`、冻结结果 `results-B.json`；按请求只交付可替换英文 Summary（`summary-B.md`）与本记录；正文与输入保持原样，未改写、未新增指标。
- 顺序：先审实质性错误，再重构摘要；摘要每个数字均须能在正文与冻结结果中定位。

## 原摘要问题（位置：paper-B.md 第 3 行 Summary）

| # | 原表述 | 证据 | 后果 | 修复 |
|---|---|---|---|---|
| 1 | "An innovative universal optimizer makes L globally optimal." | 正文 §2：no global optimality certificate over other policies；§4：mechanism is constraint-first policy switching, not a new optimization algorithm；§4：intermediate settings 未评估 | 无证据的全局最优/普适主张，且把“机制”误述为“新优化器” | 删除该框架；改为约束优先的条件切换机制 |
| 2 | "Costs drop by 12 percentage points" | 正文 §2 与 JSON `Q1.L_relative_cost_reduction=0.12`：100→88 为**相对下降 12%**，不是百分点（百分点用于率类指标） | 单位/口径错误，夸大表述 | 改为 "reduces total batch cost by 12%" |
| 3 | "service improves by 6%" | 正文 §2 与 JSON `L_service_gain_percentage_points=6`：86%→92% 为 **6 个百分点**，并非 6% 相对提升 | 百分比与百分点混用 | 改为 "a gain of 6 percentage points (86% to 92%)" |
| 4 | "proving that L should always be used in real operations" | 正文 §3：压力场景仅 R 满足 85% 下限；§1/§5：结果为 synthetic 模拟、非 field measurements、无 simulator | 与 Q2 结论直接矛盾，且把模拟结果写成实测/普适结论 | 改为条件推荐（base→L，stress→R），并保留合成数据、不可复现、未测外部场景等边界 |

## 已执行核对
- 摘要数字逐项对齐正文与 JSON：Q1 baseline 100/0.86、L 88/0.92、R 96/0.97（JSON `Q1`）；Q2 L 91/0.78、R 103/0.88（JSON `Q2`）；Q3 base→L、stress→R（JSON `Q3`）。
- 口径核对：服务下限 0.85 为强制约束；Q2 中 78%<85%、88%≥85%，故仅 R 可行；成本单位 CNY per batch、场景为 batches of 100 synthetic requests，均按原文保留。
- 未引入本轮新算指标、未造概率或置信结论。

## 未做检查（按请求豁免，不记为通过）
- 未做 PDF/官方模板核对与逐页渲染；未核对图表（正文说明无图、无 simulator）；无法复现模拟结果，状态保持“不可复现”，与正文 §5 一致。

## 结论
- `summary-B.md` 为可直接替换的 Summary：Q1 给基设置成本与服务直接结果，Q2 给压力情景可行推荐（R），Q3 给条件决策与适用边界；所有主张可追溯至正文与冻结结果。
- 因未做版面/官方规则核对，不标记为“可提交”；整体提交状态本次未评估。
