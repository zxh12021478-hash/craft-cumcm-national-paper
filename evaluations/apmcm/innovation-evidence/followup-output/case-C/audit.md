# Case-C 审查记录（audit）

- 对象：`case-C/paper.md`（16 行短论文）+ `solve.py`（22 行）+ `results.json`（8 个候选行）
- 输入哈希（SHA-256）：paper `eb73a316…fef1d2`；solve.py `536612a1…c88313e`；results.json `2f5c394e…b03a73`
- 审查依据：craft-apmcm-paper 的 `references/english-audit.md` 四遍检查 + `abstract-priority.md`
- 结论先行：**这是一个完整的有限枚举精确解，含全部 8 个候选行（含失败行）。原程序复现与独立重算两条通道结果一致，Q1/Q2 答案与 20% 参考差距全部成立。无需改正文、无需新增指标（不生成 body-patch）。**

## 0. 两条验证通道（按要求分开）

| 通道 | 做法 | 结果 |
|---|---|---|
| 原程序复现 | 原样运行 `solve.py` → `reproduced_results.json`，与原始 `results.json` 比较 | **完全相等（exact JSON equality: True）** |
| 独立数字核对 | `independent_recompute.py`（递归枚举 + 独立约束判定 + 解析下界）→ `results.json` | 全部主张一致；与原结果 0 行失配 |

## 1. 任务覆盖（Task closure）

| 原题要求 | 材料定位 | 状态 |
|---|---|---|
| Q1：从 3 个模块中选子集（每种至多 1 个），安装成本最小 | solve.py 枚举；results.json 8 行；paper 表 | 候选集完整（2^3=8） |
| 正常运行供给 ≥ 7 units/day | 约束 `total>=7` | 逐行重算 |
| 任一已装模块失效后剩余 ≥ 3 units/day | 约束 `all(residual>=3)` | 逐行重算 |
| Q2：所选设计在各单模块失效下的剩余供给 | results.json optimal_designs.single_failure_supply | A 失效→3；B 失效→4 |
| 条件集有限、非随机样本 | paper 多处声明 | 口径正确，无概率主张 |

## 2. 核对结果（verified）

### 2.1 全部 8 个候选（独立重算，含失败行）
| 设计 | 正常供给 | 成本 | 单失效剩余 | 可行性 |
|---|---:|---:|---|---|
| ∅ | 0 | 0 | — | 否（正常不足） |
| A | 4 | 7 | A→0 | 否 |
| B | 3 | 5 | B→0 | 否 |
| C | 5 | 10 | C→0 | 否 |
| **A+B** | **7** | **12** | A→3, B→4 | **是（最优）** |
| B+C | 8 | 15 | B→5, C→3 | 是 |
| A+C | 9 | 17 | A→5, C→4 | 是 |
| A+B+C | 12 | 22 | A→8, B→9, C→7 | 是 |

- 可行设计恰为 4 个：A+B 12、B+C 15、A+C 17、A+B+C 22，与论文一致。
- 唯一最优：A+B，成本 12（unique_optimum = true）。
- Q2：A 失效 → B 单独供 3（=下限，满足）；B 失效 → A 供 4（满足）；最坏指定失效剩余 = 3。
- 参考 B+C = 15；(15−12)/15 = **20%**，方向、口径与论文一致。

### 2.2 解析下界证书（独立于枚举过程）
- 所有成本 < 12 的设计（∅、B 5、A 7、C 10）正常供给均 < 7，无一可行；
- 故不存在成本低于 12 的可行设计，与枚举的最优 12 互为印证。这是对所给模型的完整有限证书，而非仅依赖 solver 状态。

## 3. 发现（无改变答案的错误）

### 3.1 已核实、可保留
- 枚举覆盖完整：8 行全部记录且失败行保留（符合"results.json records all eight rows, not just successes"）。
- 整数算术，无随机性、无学习参数、无外部样本；不可分割、容量无损相加的题设被正确实现。
- 对参考设计（capacity-first 先 C 后 B → B+C）的定位准确：正常 8，失效后 3 或 5，成本 15；并明确这只是指定比较、不是最强启发式。
- 限制声明完整：不主张硬件可靠性、失效概率、物理容量验证或多重失效/未知情形下的泛化——且明确这些限制不否定精确解。

### 3.2 保留但需标注状态
- 结果是"所给加性容量模型 + 有限偶发集"下的**精确**数学答案；`verified` 仅覆盖该模型，不延伸到任何真实硬件或未列入的失效模式（论文未越界）。
- solve.py 的 `all(v>=3 ...)` 对空设计为空集真，但空设计同时被正常约束否决，无逻辑漏洞。

### 3.3 明确不需要做的事
- 有限精确问题不需要留出数据、显著性检验或额外实验（与 english-audit 停止纪律一致）。
- 不新增指标，故不生成 `body-patch.md`。

## 4. 英文与版式检查
- 无图；符号 x_A/x_B/x_C、容量 4/3/5、成本 7/5/10、单位 CNY 与 units/day 全文一致。
- 百分比口径正确（20% 为相对 B+C 的成本下降）；"unique minimum"、"exact" 等措辞与枚举证书匹配，未把有限集最优写成无约束全局最优。
- 摘要、正文、结论数字相互一致。

## 5. 决策价值
- Q1 选 A+B（成本 12，正常 7，唯一最优）；Q2 报告 A 失效剩 3、B 失效剩 4。
- 相对指定参考 B+C 省 20%；该比较真实且具辨别力。
- 答案可直接用于题设的有限条件；不附部署、概率或外推主张。

## 6. Headline ledger

| 原文引用（精确） | 数值 token | 结果定位 | 口径/单位 | 判定 |
|---|---|---|---|---|
| "enumerate all eight subsets of three" | 8 | claim_checks.n_candidates = 8 | 2^3 完整 | verified |
| "Installing A and B costs CNY 12 and supplies 7" | 12/7 | optimum_cost / normal_supply | CNY、units/day | verified |
| "If A fails, B retains 3 … if B fails, A retains 4" | 3/4 | Q2_optimum_residual | units/day | verified |
| "unique minimum among the complete finite candidate set" | — | unique_optimum = true | 4 个可行中唯一 | verified |
| "20% less than … B+C at CNY 15" | 20%/15 | reference_reduction = 0.2 | 相对参考成本 | verified |
| 可行集 "A+B 12, B+C 15, A+C 17, A+B+C 22" | 4 行 | feasible_designs_costs | CNY | verified |
| 限制段（无硬件/概率/多失效） | — | 范围声明 | — | 合规，保留 |

## 7. 证据状态
- `verified`（双通道）：8 候选行、可行集、唯一最优 A+B、Q2 剩余、20% 参考差距。
- `unable-to-verify`（且论文未主张）：真实硬件可靠性、物理容量、未指定的多重失效、引入新模块/新概率后的答案。
- 未读取 input 与指定 skill 之外的任何材料；未修改原始输入与 skill。
