# 摘要审查记录（audit）

审查对象：input/paper.md 的原 Summary、正文 §1–§5、冻结结果 input/results.json、request.md 三问。
审查依据：craft-apmcm-paper 的 `references/abstract-priority.md` 与 `references/english-audit.md`（初稿返回阶段，仅重构摘要，不重写论文）。
结论：原摘要 6 处主张中 4 处与正文/冻结结果直接矛盾或无来源，已用 output/summary.md 整体替换；正文与 results.json 数值一致，未发现需要改正文的实质错误。本例为微型试用品，不构成完整比赛验证。

## 1. 问题覆盖（每问均有直接答案）

| 问题 | 正文定位 | 冻结结果（results.json） | 口径与证据状态 | 摘要处理 |
|---|---|---|---|---|
| Q1 未来4周需求预测样本外误差比较 | §2 | `/Q1`：horizon=4 周；20 个非重叠样本外测试目标；RMSE 单位 items；baseline 10、regression 8；相对降幅 0.2 | 同目标、合并平方误差；特征仅限预测原点可得信息；训练数据拟合系数；非分类准确率；无因果解释 | 必留：8 vs 10 items、20%、样本外/同口径 |
| Q2 容量约束下库存策略选择与成本比较 | §3 | `/Q2`：12 个预设可行候选；推荐 P；成本 120 vs 150 CNY；相对降幅 0.2；约束残差容差 1e-8；`optimality_scope` = 仅候选集内 | 同一合成需求轨迹、同等服务要求；候选集最优，非全局最优；常规优化非新算法；成本非能耗 | 必留：P、120/150 CNY、20%、1e-8、候选集限定 |
| Q3 需求扰动下建议边界 | §4 | `/Q3`：20 个预设情景（-10%~+10%）；P 在 18 个最优；`probabilities_assigned=false`；两个 +10% 情景改用 R | 情景无概率；18/20 是频率不是获胜概率；情景之间/之外未验证 | 必留：18/20、+10% 切换 R、条件性建议与未验证区间 |

## 2. 原摘要主张映射与判定

| # | 原 Summary 主张（paper.md L3） | 正文/结果定位 | 判定 | 处理 |
|---|---|---|---|---|
| 1 | "use Python, regression, and an advanced optimizer" | §3 明示 "routine optimization, not a new algorithm" | 软件罗列+夸大：advanced optimizer 无证据且与正文矛盾 | 删；只保留方法与决策作用 |
| 2 | "globally optimal strategy" | §3 "does not certify global optimality over unrestricted policies"；`/Q2/optimality_scope` | 失实：仅 12 个预设候选内最优 | 降级为 least-cost among 12 evaluated candidates |
| 3 | "reduces real-world energy consumption by 25%" | scope=synthetic；§1 无任何能耗测量、金额单位 CNY；§3 costs are not energy measurements；`/Q1`、`/Q2` 相对降幅均为 0.2 | 三重失实：成本≠能耗、合成≠实测、25% 无来源（实际同口径降幅均为 20%） | 改为 120 vs 150 CNY、20%，并声明合成、非能耗 |
| 4 | "92% forecasting accuracy" | §2 "No classification accuracy was computed"；`/Q1` 仅有 RMSE 10→8 items | 捏造指标：全文无准确率口径 | 改为样本外 RMSE 8 vs 10 items、20% |
| 5 | "wins with a probability of 90%" | §4 情景无概率；`/Q3/probabilities_assigned=false`；18/20 | 范畴错误：有限情景频率≠概率 | 改为 18/20 预设情景，并明确不是概率 |
| 6 | "excellent robustness and wide applicability" | §4–§5：仅测 -10%~+10% 预设情景；合成数据，外部未验证 | 空泛、超出证据 | 删；结尾给条件性建议（P 基础情形，+10% 切 R）与外部验证边界 |

## 3. 数值复核（仅基于冻结记录的算术）

- (10−8)/10 = 0.20，与 `/Q1/relative_rmse_reduction` 一致；(150−120)/150 = 0.20，与 `/Q2/relative_cost_reduction` 一致。基线非零、口径可比，相对降幅可在摘要中引用。
- 单位、分母、方向、作用域已逐项对齐：RMSE 单位 items、成本单位 CNY、20 个测试目标、12 个候选、20 个情景。
- 正文 §1–§5 与 results.json 全部数值一致，未发现矛盾；正文自身限定语（样本外、候选集、无概率、非能耗、非因果）齐备。

## 4. 未验证项（unable-to-verify / supported-not-reproduced）

- 未提供可执行代码：RMSE、成本与残差检查只能核内部一致性，状态为 supported-not-reproduced；按 fixture 附录说明，不得标记代码复现完成。
- 未提供图表与 PDF：无图内文字/坐标轴/版面可视检查；本 fixture 不适用 PDF 逐页检查。
- 官方模板与页数规则未提供：summary.md 为工作稿，标题层级、字数与分页须在官方模板发布后按实际渲染空间核对，未套用任何固定词数。
- 25% 能耗、92% 准确率、90% 概率在正文与 results.json 中无任何可能来源，属原摘要捏造，非"待验证"。

## 5. 正文修改建议

- 无需改正文数值或结论：正文与冻结结果一致，限定语正确。唯一必做动作是用 summary.md 原封替换 L3 的 Summary。
- 可选（非必须）：正文 §2 已说明无分类准确率，替换摘要后该防线不再被摘要违反，无需改动。

## 6. 新摘要变更说明

- 提亮：三问直接答案形成链（RMSE 8 vs 10 items → P 120 vs 150 CNY、1e-8 约束通过 → 18/20 情景、+10% 切 R）。
- 删/降级：全局最优→候选集最优；25% 实测节能→20% 合成成本下降（CNY，非能耗）；92% 准确率→RMSE 对照；90% 概率→18/20 情景频率并声明非概率；删除软件清单与 excellent robustness / wide applicability。
- 保留边界：合成数据、样本外有限测试集、情景无概率、情景间/外未验证、非因果、需外部部署验证。
- 尚缺：官方模板核对与代码复现（见第 4 节），在补齐前不标记可提交。
