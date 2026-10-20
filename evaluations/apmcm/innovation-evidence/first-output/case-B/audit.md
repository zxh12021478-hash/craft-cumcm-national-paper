# Case-B 审查报告（audit）

对象：`input/case-B/paper.md` + `runs.csv`（完整短论文，非摘要判断）。
方法：按 craft-apmcm-paper 第 2 阶段四遍流程；本地重算与原程序/实测验证严格分开。
重算脚本：`recompute.py`；机器结果：`results.json`。

---

## 0. 结论先行

- **论文主张与数据一致，可保留：在 12 个 held-out 合成评估日上，R 相对 P 完整成本下降 5%（11,400 vs 12,000 CNY），服务率 96% vs 94%（+2 个百分点），两策略每日均满足 90% 服务下限与全部记录硬约束，12 个成对日比较全部利于 R。**
- 推荐范围被论文正确限定于该测试集；未主张显著性、未来概率、全局最优或硬件性能。
- 无需新增指标，故不写 body-patch；无需为该限定结论补做实验。

## 1. 任务闭合（Task closure）

| 任务要求 | 证据位置 | 状态 |
|---|---|---|
| P 与 R 在评估日满足库存/供给硬约束 | paper Results；CSV `complete`/`hard_feasible` | 24/24 行均为 1，**闭合** |
| 每日至少服务 90% 请求 | paper Results；CSV `served`/`requests` | P 每日 94%、R 每日 96%，均 ≥90%，**闭合** |
| 最小化完整运营成本 | CSV `cost_cny`/`cost_complete` | 全部 `cost_complete=1`，同成本项，R 更低，**闭合** |
| 在 P 与 R 间作出选择 | paper Conclusion | 选 R，限定于 12 日测试集，**闭合** |

## 2. 数字核对（本地重算，fixture 内部一致性）

| 指标 | 论文说法 | 重算结果（results.json） | 判定 |
|---|---|---|---|
| 总成本 P / R | 12,000 / 11,400 | 12,000 / 11,400 | `verified` |
| 相对降幅 | 5% | (12,000−11,400)/12,000 = 0.05 | `verified` |
| 聚合服务率 P / R | 94% / 96% | 11,280/12,000 = 94%；11,520/12,000 = 96% | `verified` |
| 服务率增益 | 2 个百分点 | 96%−94% = 2 pp（百分点用法正确） | `verified` |
| 每日 90% 下限 | 每日均满足 | 日最低 P 94%、R 96%，无低于 90% 的日 | `verified` |
| 成对日比较 | 12 个全部利于 R | 每日成本差 R−P = −50（12/12）；服务差 +20 | `verified` |
| 完整运行/可行性 | 12 对均完整可行 | 24/24 complete=1、hard_feasible=1、cost_complete=1 | `verified` |
| 评估单位 | 12 个日为单位 | 12 日（非 12,000 次独立重复） | 论文口径正确 |

## 3. 科学主张与 headline ledger

| # | 原文主张 | 状态 | 说明 |
|---|---|---|---|
| 1 | "reduced total operating cost by 5%, from CNY 12,000 to 11,400" | `verified`（CSV 重算） | 比较对象、方向、口径齐全 |
| 2 | "Service rose from 94% to 96%, a gain of 2 percentage points" | `verified` | 百分点与百分比未混用 |
| 3 | "both policies met the 90% daily service floor and all recorded hard constraints" | `verified` | 逐日检查通过 |
| 4 | "recommended over P for this tested set" | `verified` + 范围恰当 | 推荐与证据范围一致 |
| 5 | "Generalization beyond the synthetic generator and real implementation remain unverified" | 恰当的边界声明 | 未过度外推 |
| 6 | 30 个开发日调参、6 配置、评估前冻结、评估日未参与调参 | `supported-not-reproduced` | 论文称有日志记录，但本夹具未提供日志/实现，无法独立复核 |
| 7 | R 的 reserve-release 机制与方程忠实度 | `unable-to-verify` | 无源码；论文已主动声明 |
| 8 | 不主张置信区间/显著性/未来可行性 | 处理正确 | 日成本差零方差，t 型区间退化；论文未做任何显著性声明，无需补造 |

## 4. 英文与版式

- 摘要、正文、结论数字一致；比较参照、时态、情态词使用克制（"is therefore recommended … for this tested set"）。
- 百分比与百分点区分正确；"held-out" 有明确流程叙述（虽不可独立复核）。
- 无图表；CSV 为唯一结果源，字段单位与论文一致。

## 5. 决策价值

- **基线公平性**：P、R 同开发日、同配置数、同停止规则、同成本定义、成对同输入，比较口径公平（流程属论文自述）。
- **无消融但未过度归因**：论文明确声明不是对机制的完整因果归因，与证据匹配。
- **推荐**：维持论文推荐——在该 12 个 held-out 合成日上选 R；任何超出该范围的结论都需要新计算（见 `next-handoff.md`）。

## 6. 未验证事项（状态保留）

- 冻结/调参流程的独立证据：`supported-not-reproduced`（无开发日志）。
- R 的机制与方程忠实度、成本项明细：`unable-to-verify`（无源码）。
- 对未见需求/真实硬件的泛化：`unable-to-verify`，论文已声明，不影响当前限定结论。
- 本地重算仅证明 CSV 内部算术一致，不构成实证验证。
