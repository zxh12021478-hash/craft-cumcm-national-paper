# Case-A body patch（正文/结果修订，先于摘要生效）

说明：本文件仅给出可直接替换的英文正文段落与修正后结果表；数字均由 `recompute.py` 从原始 `runs.csv` 重算得到（见 `results.json`），属于**夹具内部一致性核对**，不验证缺失的实现，也不是 held-out 验证。原始输入不覆盖、不修改。

---

## 1. 替换 Results 节中的汇总表与相关文字

**原文问题**：节省表只汇总 8 个 quiet 场景却以整体结论呈现；4 个 boundary 场景被排除；可靠性 90% 与运行日志不符。

**替换为：**

> The accompanying runs.csv records the final selected configurations of B, T and TM. Table 1 reports complete costs only for runs that completed and satisfied every recorded hard constraint; an incomplete run is not a valid dispatch plan and contributes no valid total cost.
>
> **Table 1.** Complete operating cost (CNY) and hard-constraint pass counts by scenario group.
>
> | Group | Scenarios | B feasible / cost | T feasible / cost | TM feasible / cost |
> |---|---|---|---|---|
> | quiet | 8 | 8 / 800 | 8 / 760 | 8 / 640 |
> | peak | 8 | 8 / 800 | 8 / 760 | 8 / 1,040 |
> | boundary | 4 | 4 / 400 | 4 / 380 | 0 / not valid (4 runs terminate with negative terminal inventory; logged partial cost of 10 CNY each is excluded) |
> | **all 20** | 20 | **20 / 2,000** | **20 / 1,900** | **16 / no valid total** |
>
> TM's cost is 20% lower than B's only inside the quiet subset (640 vs 800). In the peak subset TM costs 30% more (1,040 vs 800), and TM produces no valid plan on any boundary scenario. On the sixteen scenarios where all three policies completed, B costs 1,600, T costs 1,520 and TM costs 1,680, so TM is 5% more expensive than B and 10.5% more expensive than T under the same complete-cost definition. Across all twenty valid scenarios, T costs 1,900 versus 2,000 for B, a 5% reduction.
>
> The hard-constraint pass rate on this scenario set is 20/20 for B, 20/20 for T and 16/20 = 80% for TM (the pooled policy-scenario rate is 56/60 = 93.3%). The previously stated 90% figure is not supported by the run log. Because the scenario generator supplies no probability law and the labels describe the generator rather than a frequency distribution, this pass rate is a set-specific descriptive count, not a probability of reliable deployment.

## 2. 修订 Methods 节中选择口径的表述（事实不变，补定性）

**在现有 Methods 段末尾补充：**

> Selecting configurations on the same twenty scenarios used for the final comparison makes every reported cost an in-sample, selection-set result. TM's selection score discarding terminated runs and its ten-fold larger configuration budget (60 vs 6 for T) are design confounders; without a matched-budget comparison and an M-on/M-off ablation on the same backbone, no observed difference can be attributed to module M.

## 3. 替换 Discussion and conclusion 的推荐段

**替换为：**

> TM cannot be recommended in its current form: it violates the terminal-inventory hard constraint on 4 of 20 scenarios and, under the common complete-cost definition, is more expensive than both B and T on the scenarios it completes. The claim that module M causes the improvement is unsupported—T alone (no M) is feasible on all twenty scenarios and 5% cheaper than B, while the M effect was never isolated and the budgets were unequal. For the specified scenario set we recommend T over B, with TM's look-ahead module M retained only as an unverified hypothesis. All figures, including T's 5% edge, are selection-set results; no held-out evaluation, deployment probability, computation-time comparison or global-optimality claim is made.

---

## 修订影响的下游主张清单

- 撤回："20% operating-cost saving"（整体口径）→ 改为 quiet 子集内 20%。
- 撤回："90% reliability" 及 "probability of reliable deployment" → 改为 TM 80%、B/T 100% 的集合内描述计数。
- 撤回："superiority is caused by the look-ahead module"、"T's contribution assumed negligible" → 因果归因不成立。
- 撤回："recommended for all demand conditions" → 当前推荐 T，且仅限指定场景集。
- 保留：B/T 全部 20 场景可行、T 完整成本 1,900 vs B 2,000（-5%）；TM 已完成 16 场景的记录成本（作为夹具记录）。
