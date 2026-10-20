# Case-B 审查记录（audit）

- 对象：`case-B/paper.md`（16 行短论文）+ `case-B/runs.csv`（12 天 × 2 策略 = 24 行）
- 输入哈希（SHA-256）：paper `fa408a93…4f3b9143`；runs.csv `be0b18c9…08bdfd3`
- 审查依据：craft-apmcm-paper 的 `references/english-audit.md` 四遍检查 + `abstract-priority.md`
- 数字核对：`recompute.py` → `results.json`（本地、独立重算；本例无原始程序，属数字核对）
- 结论先行：**这是一个口径正确、范围克制的有限描述性对比。全部 headline 数字可由 CSV 重算复现，推荐 R 用于"所测试的 12 个合成日"成立。无需改正文、无需新增指标（不生成 body-patch）。**

## 1. 任务覆盖（Task closure）

| 原题要求 | 材料定位 | 状态 |
|---|---|---|
| 在评估日之间选择 P / R | runs.csv；paper Results | 12 个配对日齐全 |
| 每日满足库存与供给硬约束 | runs.csv `complete`/`hard_feasible` | 24/24 全部满足 |
| 每日至少服务 90% 请求 | runs.csv `requests`/`served` | P 94%、R 96%，全部 ≥ 90% |
| 最小化完整运营成本 | runs.csv `cost_cny`（cost_complete 均为 1） | 完整口径，合计可复算 |
| 不得作真实部署/获奖主张 | paper Summary 末句、Conclusion | 范围声明完整合规 |

## 2. 核对结果（verified，全部来自 runs.csv）

| 指标 | P | R | 判定 |
|---|---:|---:|---|
| 完整成本合计（12 天，CNY） | 12,000 | 11,400 | 降幅 (12000−11400)/12000 = **5%** ✓ |
| 总服务率 | 11,280/12,000 = 94% | 11,520/12,000 = 96% | **+2 个百分点** ✓ |
| 每日服务率区间 | 94%（无波动） | 96%（无波动） | 均高于 90% 下限 ✓ |
| 完整且可行的运行 | 12/12 | 12/12 | ✓ |
| 配对日成本有利于 R | — | 12/12 | ✓ |
| 配对日服务有利于 R | — | 12/12 | ✓ |

## 3. 发现（无改变答案的错误）

### 3.1 已核实、可保留
- Summary 与 Results/Conclusion 数字一致：12,000→11,400、5%、94%→96%、+2pp、90% 下限、12/12 可行。
- 方法口径正确：开发日（30 天）与评估日（12 天）分离；双方等额配置数（6）、同等特征、停止规则与成本定义；配对行对应同一天与同一输入；成本覆盖完整日。
- 范围克制到位：明确不做显著性检验、不做未来可行性概率或现场主张；明确指出评估单位是 12 个天、12,000 个请求不是独立重复；明确不声称全局最优、不把收益逐项归因于孤立机制。这些表述与证据边界一致。

### 3.2 保留但需标注状态（不影响推荐）
- **冻结声明**：日志记录两配置在评估日生成前已冻结，但无源码/无实现可独立核验，按 `supported-not-reproduced` 处理；作为 fixture 的给定条件可用于描述性结论。
- **机制保真度**：R 的 reserve-release 方程无实现可查，"改变储备释放时序"作为机制描述可保留；方程正确性按 `unable-to-verify`。
- **零方差**：12 天数值完全相同，属确定性 fixture；这是对固定实例的描述，不构成分布、置信区间或可推广性证据。原论文未越界解读，无需修复。

### 3.3 明确不需要做的事
- 不需要为诚实报告该有限描述性对比而补显著性检验或扩大实验（与 english-audit 的"不得把审查变成无条件的再调参/消融/留出实验链"一致）。
- 不需要新增指标，因此不生成 `body-patch.md`；现有 Results 表与摘要主张已被数据支持。

## 4. 英文与版式检查
- 无图；术语 P/R、reserve release、service floor 全文一致；单位 CNY、百分比与百分点使用正确（"2 percentage points" 未写成 2%）。
- 未发现占位符或内部流程文字；摘要、正文、结论之间无相互矛盾。

## 5. 决策价值
- 在 12 个留出合成日上，R 同时满足硬约束与 90% 服务下限，且成本低 5%、服务高 2pp，配对差异 12/12 同向。
- **推荐：对该测试集选择 R**。该推荐不覆盖生成器之外的泛化、真实硬件/实现表现；这些限制论文已如实陈述，不构成对有限结论的否定。

## 6. Headline ledger

| 原文引用（精确） | 数值 token | 结果定位 | 口径/单位 | 判定 |
|---|---|---|---|---|
| "reduced total operating cost by 5%" | 5% | claim_checks.cost_reduction = 0.05 | 12 天合计，CNY | verified |
| "from CNY 12,000 to 11,400" | 12000/11400 | per_policy.total_cost | 完整成本 | verified |
| "Service rose from 94% to 96%, a gain of 2 percentage points" | 94/96/2pp | claim_checks.service_rate_* | 聚合服务率；百分点 | verified |
| "both policies met the 90% daily service floor and all recorded hard constraints" | 90% | daily_service_min；hard_feasible | 每日口径 | verified |
| "All twelve paired cost differences favor R" | 12 | claim_checks.paired_days_favoring_R_cost | 天为单位 | verified |
| "Generalization … remain unverified" | — | 范围声明 | — | 合规，保留 |
| "configurations were frozen before the twelve evaluation days" | — | 无实现 | 冻结日志 | supported-not-reproduced |

## 7. 证据状态
- `verified`：全部成本/服务率/下限/配对计数（CSV 重算）。
- `supported-not-reproduced`：配置先冻结后评估的流程声明。
- `unable-to-verify`：R 机制方程与实现保真度（无源码）；生成器之外的泛化与真实性能（未主张）。
- 未读取 input 与指定 skill 之外的任何材料；未猜测预期答案。
