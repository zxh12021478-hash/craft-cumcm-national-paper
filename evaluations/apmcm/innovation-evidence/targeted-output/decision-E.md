# decision-E：固定骨干与参数配置下，模块 M 是否降低给定场景成本

## 问题边界（本次只回答这一个条件性问题）

在 **P+M 搜索选中的那个骨干与参数配置**下，M 开/关对**这批固定给定场景集**的平均成本影响。不问跨骨干主效应、不问搜索预算效应、不问未见场景/真实部署，不做全因子实验。

## 已支持事实（保留，不得丢失或改写）

- P 搜索 2 个配置后的选中方案，在固定给定场景集上平均成本 **100 CNY**；
- P+M 搜索 20 个配置后的选中方案，在**同一**场景集上平均成本 **90 CNY**；
- 两方案记录均完整、均满足题定硬约束，信息与成本口径相同。
- 口径限定：100 vs 90 同时混杂了**不同搜索预算（2 vs 20）与不同选中参数**，它只描述两套**搜索策略的结果差**，**不能归因给模块 M**。在补算完成前，M 的条件效应状态为 `unable-to-verify`，禁止直接写“M 降低 10 CNY”。

## 最小必要核对 / 补算（按顺序，能不新算就不新算）

1. **取回冻结对象**：P+M 选中方案的骨干标识、完整参数向量、M 的确切开关方式、场景集与成本函数（源码与准确配置已说明可取得，取得后固化版本/哈希）。
2. **先查现有完整记录**：是否已存在“同一骨干、同一参数、M=off、同一场景集、同一成本口径”的逐场景评估。若有，直接提取配对成本，**无需任何新实验**。
3. **若无记录，执行唯一一次确定性补算**：冻结 P+M 选中的骨干与参数，**禁止重新搜索/调参/换种子**，仅切换 M on/off，在同一给定场景集上逐场景重算；分别校验两状态的硬约束；记录逐场景成本、逐场景差值 `d_i = C_off,i − C_on,i` 与均值 `Δ = mean(d_i)`。
4. 有限给定场景集上的确定性配对差，**不追加显著性检验**；不做等预算重搜（与本条件问题无关）。

## 停止条件（分支即结论，一次配对评估后停止）

- **两状态均可行**：`Δ>0` → 在该固定配置下 M 降低这批场景成本（报告实测 Δ 及逐场景符号，注明仅对该配置与该场景集成立）；`Δ=0` → 无差异；`Δ<0` → M 升高成本。**Δ 为待测量，交接时不填数值、不预写实验结果。**
- **M=off 在该冻结配置下违反硬约束**：like-for-like 成本差无定义；结论改写为“M 在该固定配置下为可行性所必需”，如实报告，不与成本差混写。
- **源码/准确配置无法取得，或 M 无法在选中后单独关闭（参数仅在 M 开启时有定义）**：模块效应保持 `unable-to-verify`；仅可报告整套搜索策略 100→90 的有限差异（明确标注为 policy comparison），不归因 M，停止。

## 交给执行人 / Modex 的下一步（可直接执行）

> Retrieve and freeze the exact backbone ID, full parameter vector, M toggle, scenario set and cost function of the design selected by the P+M search (20-config run). First inspect existing complete records for an M-off evaluation at that identical backbone/parameter vector on the identical scenario set under the identical cost caliber; if present, extract paired per-scenario costs without new runs. Otherwise perform exactly one deterministic re-evaluation with the backbone and parameters frozen (no re-search, no tuning): M on vs M off, same scenarios, same inputs, same cost accounting; verify hard constraints in both states; report per-scenario costs, per-scenario differences d_i and mean Δ, plus feasibility status. Conclude only for this fixed configuration and the given scenario set; do not generalize across backbones, search budgets, unseen scenarios or deployment; do not report significance tests; do not fill Δ before the run. If M-off is infeasible or cannot be isolated, mark the module effect unable-to-verify and report only the 100-vs-90 policy-level difference. Return run configuration, code/version locators and per-scenario traceability.

## 停止条件（汇总）

一次同配置 on/off 配对评估完成（或确认无法隔离）即关闭；任何向跨骨干、跨预算、未见场景的扩展均标为可选，不阻塞本题交稿。
