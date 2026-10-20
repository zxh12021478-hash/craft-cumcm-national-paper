# Case-A 审查记录（audit）

- 对象：`case-A/paper.md`（16 行短论文）+ `case-A/runs.csv`（20 场景 × 3 策略 = 60 行）
- 输入哈希（SHA-256）：paper `e879fcb3…7c429b`；runs.csv `86fa3162…7d738aa`
- 审查依据：craft-apmcm-paper 的 `references/english-audit.md` 四遍检查 + `abstract-priority.md`
- 数字核对：`recompute.py` → `results.json`（仅本地、独立重算；本例无原始程序，属数字核对，非程序复现）
- 结论先行：**摘要的四项核心主张（20% 节省、90% 可靠率、M 归因、全工况推荐）均不成立；当前应推荐 T（样本内、待留出验证），不推荐 TM；M 未被证明改善策略，且在 peak/boundary 上观测到损害。**

## 1. 任务覆盖（Task closure）

| 原题要求 | 材料定位 | 状态 |
|---|---|---|
| 选择满足全部硬约束（需求不可弃、期末库存非负）的调度策略 | runs.csv `complete`/`hard_feasible`/`cost_complete`；paper Results | 数据齐，但摘要所选 TM 在 S17–S20 违反硬约束 → **答案无效** |
| 在满足约束下最小化每场景完整运营成本（CNY） | runs.csv `cost_cny`；paper Results | 可行集合内可重算；TM 成本为部分日志，不可比 |
| 说明自适应模块 M 是否改善策略 | paper Methods/Discussion | 仅 T 与 TM 配对；无 M-without-T；调参预算不等；**无法作因果归因** |
| 材料完整性 | paper Methods 自陈：无独立评估集、无逐配置评分、无源码 | 缺口已由原论文自陈，按 `unable-to-verify` 保留 |

## 2. 可保留的结果（verified，全部来自 runs.csv 重算）

- 原始记录内部一致：`complete=0` 行同时 `hard_feasible=0`、`cost_complete=0`，无矛盾。
- B、T 完成全部 20 个场景且全部通过硬约束；T 每场景 95 CNY vs B 100 CNY，样本内低 5%（合计 1900 vs 2000）。
- TM 在 quiet 8 个场景每场景 80 CNY（描述性事实）。
- Results 段落如实报告了 S17–S20 的失败与部分成本口径，未隐瞒。

## 3. 改变答案的发现（按严重度排序）

### F1 TM 不是可行方案，"全工况推荐"错误（answer-changing）
- 位置：paper Summary 第 1 句；Results 第 2–4 句；CSV 中 S17–S20 的 TM 行。
- 证据：S17–S20 TM 行 `complete=0, hard_feasible=0, cost_complete=0, cost_cny=10`，原因为期末库存为负（4 个 boundary 场景全部失败）。paper 自己也承认 "Such a run is not a valid dispatch plan"。
- 后果：硬约束是任务的第一门槛，任何不可行方案不能进入成本比较；"validated policy … recommended for all demand conditions" 与数据直接矛盾。
- 最小修复：可行候选仅保留 B、T；推荐与摘要中删除 TM 的部署表述。
- 复核：候选策略必须满足全部 `hard_feasible=1` 且 `cost_complete=1`；见 `results.json` overall。

### F2 "20% 节省"只在 quiet 子集成立；完整对比下 TM 更贵（answer-changing）
- 位置：paper Results 第 5 句（仅对 quiet 求和）；Summary 第 1 句。
- 证据（重算）：
  - quiet：B 800、T 760、TM 640 → TM 对 B 为 −20%（论文数字在此口径下正确）；
  - peak（S09–S16）：B 800、T 760、TM 1040 → TM 对 B **+30%**；
  - boundary：TM 无完整成本（4×10 仅为部分日志，合计 40）；
  - 在 TM 完成的 16 个场景上合计：TM 1680 vs B 1600（**+5%**）vs T 1520（**+10.5%**）。
- 后果：20% 是挑选有利子集（cherry-picking），且遗漏 boundary；不能作为总体节省主张。
- 最小修复：展示全部 20 场景的分组小计 + 可行策略完整合计（TM 合计标为"不可定义"），见 `body-patch.md`。
- 复核：`results.json` → cells / claim_checks。

### F3 "90% 可靠率"数字错误，且不能解释为概率（answer-changing）
- 位置：Summary 第 1 句；Results 末两句。
- 证据：按论文自定口径（通过硬约束的运行占比），TM = 16/20 = **80%**（`results.json` overall. TM.feasible_share = 0.8），不是 90%；B、T 均为 100%。
- 概率解读问题：题目明确场景标签只描述生成器、无未来场景概率律；80% 只是该固定场景集上的覆盖率，不是 "probability of reliable deployment"。
- 最小修复：改为"本场景集上 80%（16/20）"，删除概率解读；可可靠率本身不改变 F1 的不可行结论。
- 复核：重数 CSV 中 policy=TM 且 hard_feasible=1 的行数 = 16。

### F4 选择与评估同一批场景，且选择评分忽略失败运行（answer-changing / 方法缺陷）
- 位置：paper Methods 第 3–6 句。
- 证据：20 个场景既用于 T（6 配置）与 TM（60 配置）的选择，又用于最终对比，无独立评估集；TM 的选择分数 "ignores runs that terminate before the end"。
- 后果：
  1. 样本内选择偏差：报告的差距是选择结果，不是性能估计；
  2. 忽略失败运行在硬约束问题上是错误规则——失败配置应按不可行（无限成本）处理，而该规则恰好让不可行配置可能胜出；
  3. 逐配置评分与源码未保留，选择过程本身无法核实。
- 最小修复：选择规则改为失败即不可行；配置冻结后再生成新场景做留出评估；保留逐配置评分。
- 复核：留出运行中被推荐策略的可行率必须为 100%（见 next-handoff 验收）。

### F5 "优越性由 M 导致"无证据；T 的贡献被错误假定为可忽略（归因错误）
- 位置：Summary 第 2 句；Discussion 第 1–2 句。
- 证据：
  - T 在全部 20 个场景对 B 稳定低 5%（95 vs 100），T 的贡献不可忽略；
  - M 直接对照（TM 对 T，条件于 T）：quiet 95→80（−15）、peak 95→130（**+35**）、boundary 95 可行 → 不可行；
  - 无 M-without-T（B+M）变体，T 与 M 的交互无法分离；
  - 调参预算 6 vs 60 不等，比较受搜索预算混淆。
- 最小修复：只陈述上述配对观测；删除因果归因；如需归因，补 2×2 因子（B、T、B+M、TM）与等额预算。
- 复核：四变体在同一场景、同一预算下的配对成本与可行率（见 next-handoff）。

### F6 次要
- 未测计算时间、未比较等额调参预算（原论文已自陈）；未声称全局最优（措辞合规）；无图表，无轴/图例问题；单位（CNY）无混用。

## 4. 英文与版式检查
- 无图、无公式排版；术语 B/T/TM、quiet/peak/boundary 全文一致。
- 主要问题是 Summary 与 Results 自相矛盾：摘要的 20%/90%/因果/全工况在 Results 中均无对应支持（Results 反而提供反证）。
- Results 段落自身的口径说明（partial cost、非有效计划）是诚实且准确的，应保留。

## 5. 决策价值与当前推荐
- 本场景集上，可行策略只有 B、T；T 完整成本合计 1900 < B 2000，且每场景均不劣于 B。
- **当前推荐：T（限定为该合成 fixture 的样本内描述性结果）**；不得推荐 TM，不得称"全工况"或"已验证"。
- 对 M 的回答：没有证据表明 M 改善策略；在现有数据中 M 与 peak 成本上升和 boundary 不可行同时出现。M 的前瞻机制可保留为待检验假设，但需按 next-handoff 修正选择规则并做留出评估。

## 6. Headline ledger

| 原文引用（精确） | 数值 token | 结果定位 | 口径/单位 | 判定 |
|---|---|---|---|---|
| "delivers a 20% operating-cost saving" | 20% | claim_checks.quiet_only_saving_TM_vs_B.saving = −0.20 | 仅 quiet 8 场景，CNY | 仅在该子集成立；总体主张撤回 |
| "maintaining 90% reliability" | 90% | overall.TM.feasible_share = 0.80 | 本场景集通过硬约束占比 | 数字错误，应为 80% |
| "probability of reliable deployment" | — | 题目无概率律 | 覆盖率≠概率 | 撤回 |
| "In the eight peak scenarios, B costs 800 and TM costs 1040" | 800/1040 | cells 下 peak 小计 | CNY，TM +30% | 核对一致（原文未用于摘要） |
| "superiority is caused by the new look-ahead module" | — | paired.TM_vs_T | 无 M-without-T、预算不等 | 归因不成立，撤回 |
| "recommended for all demand conditions" | — | boundary TM 0/4 可行 | 硬约束门槛 | 撤回 |
| T 95 / B 100（隐含全场景） | 95/100 | overall.B/T | 20 场景完整成本 | 核对一致 |

## 7. 证据状态
- `verified`（CSV 重算）：各分组小计、配对差异、可行率、完整成本合计。
- `unable-to-verify`：逐配置选择结果与调度方程保真度（无源码、无评分）；任何样本外/实测表现。
- `withdrawn`：总体 20% 节省、90% 与概率解读、M 因果归因、"all demand conditions" 推荐。
- 本记录不含对预期答案的猜测；未读取 input 与指定 skill 之外的任何材料。
