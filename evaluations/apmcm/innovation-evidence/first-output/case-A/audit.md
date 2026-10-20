# Case-A 审查报告（audit）

对象：`input/case-A/paper.md` + `runs.csv`（完整短论文，非摘要判断）。
方法：按 craft-apmcm-paper 第 2 阶段（返回稿审查）四遍流程；本地重算与原程序/实测验证严格分开。
重算脚本：`recompute.py`；机器结果：`results.json`。

---

## 0. 结论先行

- **当前推荐 T，不推荐 TM。** B、T 在全部 20 个场景完整且满足全部记录硬约束；T 完整成本 1,900 vs B 2,000 CNY，同口径低 5%。TM 在 4 个 boundary 场景终端库存为负、运行不完整，不构成合法调度方案，且在 16 个共同完成场景上比 B 贵 5%、比 T 贵 10.5%。
- **M 的创新主张不成立（当前证据下）。** 无 M 消融、T 与 TM 调参预算不等（6 vs 60）、选择与最终比较同用 20 场景、TM 选择评分丢弃失败运行；M 只能作为待验证假设。
- 论文标题数字两处失真：20% 节省仅为 quiet 子集；90% 可靠性与日志不符（TM 实为 80%，池化 93.3%）。

## 1. 任务闭合（Task closure）

| 任务要求 | 证据位置 | 状态 |
|---|---|---|
| 满足全部硬约束（不弃负荷、终端库存非负） | paper Results；CSV `complete`/`hard_feasible` | B、T 20/20 满足；TM 仅 16/20，boundary 4 个违约 → **未闭合** |
| 最小化每场景完整运营成本（CNY） | paper Results；CSV `cost_cny`/`cost_complete` | 不完整运行的 10 CNY 只是部分成本，不能计入完整成本比较 |
| 解释自适应模块 M 是否改善策略 | paper Discussion | 给出了因果断言，但无对照支撑 → **未闭合** |
| 场景标签≠频率分布，无未来概率律 | paper Task/Discussion | 论文已承认，却仍给 90% 部署概率解读，自相矛盾 |

## 2. 数字核对（本地重算，fixture 内部一致性）

| 指标 | 论文说法 | 重算结果（results.json） | 判定 |
|---|---|---|---|
| quiet 子集 B vs TM | 800 vs 640，-20% | 800 vs 640，-20% | 算术成立，**仅 quiet 子集** |
| peak 子集 B vs TM | 800 vs 1040 | 800 vs 1040，TM **贵 30%** | 论文列了但未用于推荐，方向不利 |
| boundary（4 个） | 被排除在节省表外 | B 400、T 380 均可行；TM 0/4 可行，4×10 为部分成本 | TM **硬约束违约** |
| 全 20 场景完整成本 | 未给整体数 | B 2,000；T 1,900；TM 无合法总额（日志口径合计 1,720 含 40 部分成本） | TM 无可比总额 |
| 16 个共同完成场景 | 未给 | B 1,600；T 1,520；TM 1,680 | TM 比 B 贵 5%、比 T 贵 10.5% |
| B vs T（20 场景） | 未给比较 | 1,900 vs 2,000，T 省 5% | 成立 |
| 可靠性 | 摘要 90% | TM 16/20=**80%**；B/T 100%；池化 56/60=93.3% | **90% 无法复现** |
| 部署概率 | 解读为 90% 概率 | 无概率律，不可计算 | 主张不成立 |

状态说明：以上均为 `verified`（就给定 CSV 夹具的内部一致性而言）。数字核对**不**证明调度实现与所述方程一致。

## 3. 科学主张与 headline ledger

| # | 原文主张（摘引） | 口径/来源 | 状态 | 最小修复 |
|---|---|---|---|---|
| 1 | "delivers a 20% operating-cost saving" | 仅 quiet 8 场景求和 | `verified`（子集算术）/ 整体主张 refuted | 限定为 quiet 子集；补全组表 |
| 2 | "maintaining 90% reliability" | CSV 硬约束通过率 | **refuted**：TM 80%、池化 93.3% | 改为 80%（TM）并报告分母 |
| 3 | "probability of reliable deployment" | 无概率律 | 不成立（原则性错误） | 删除概率解读，保留集合内计数 |
| 4 | "superiority is caused by the new look-ahead module" | 无 M-without-T、无等预算对照、同集选择 | `unable-to-verify` → 因果主张撤回 | 等预算 + M 开关消融 + held-out |
| 5 | "T's contribution is assumed negligible" | T 实际 20/20 可行且比 B 省 5% | 与数据矛盾 | 撤回，改为 T 是当前最优合法策略 |
| 6 | "recommended for all demand conditions" | peak 更贵、boundary 违约 | refuted | 降级为集合内、按条件推荐 |
| 7 | TM 选择评分忽略提前终止运行 | paper Methods 自认 | 设计缺陷（幸存者偏差），`supported`（论文自认） | 选择评分加硬可行性门 |
| 8 | 配置/评分/源码 | 明确未保留 | `unable-to-verify` | 下一阶段保留每配置评分与代码 |

## 4. 英文与版式

- 正文数字内部自相矛盾（摘要 90% vs 结果节的 16/20 事实；整体 20% vs 仅 quiet 求和），属实质错误而非语言问题。
- 术语：reliability 被混用为通过率与部署概率；logged partial cost 与 complete cost 未在比较表中区分。
- 无图表；CSV 为唯一结果源。修复后需同步替换 Summary、Results 表与 Conclusion（已在 `body-patch.md` 给出）。

## 5. 决策价值（基线公平性 / 消融 / 失效域）

- **基线公平性**：B、T 使用同一信息集；但 T 6 配置、TM 60 配置且同 20 场景选择，预算与数据泄漏双重不对等。
- **消融缺失**：T 与 TM 同时改变预算与 M，无法分离；无 M-without-T。
- **失效域明确**：TM 在 boundary 全部违约、在 peak 成本更高；其优势仅出现在 quiet。
- **可保留结果**：B/T 的 20 场景可行性与成本记录；T 相对 B 的 5% 记录优势（注意仍为选择集内结果）；TM 已完成 16 场景的记录成本。
- **推荐**：在指定场景集上采用 T；M 为未验证假设，TM 修复 boundary 可行性并通过等预算 held-out 对照前不得推荐。

## 6. 未验证事项（状态保留）

- 调度方程与实现忠实度：`unable-to-verify`（无源码、无每配置评分）。
- 选择流程与 6/60 配置细节：论文自述，`supported-not-reproduced`。
- 任何样本外/泛化表现、部署概率、计算时间：`unable-to-verify`，且概率主张在无概率律下不可计算。
- 本地重算仅证明 CSV 内部算术一致，不构成实证验证。
