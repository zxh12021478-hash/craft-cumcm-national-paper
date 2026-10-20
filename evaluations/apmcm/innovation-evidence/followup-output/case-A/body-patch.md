# Case-A 正文/结果修订（body-patch）

本文件提供正文修订块，**不覆盖原始材料**；修订落实后，可替换摘要（`summary.md`）才可使用其中数字。数字来源：`recompute.py` → `results.json`。

## 修订 1：替换 Results 章节（整段替换原 "## Results" 小节）

```markdown
## Results
The accompanying runs.csv lists the final selected configurations for the
twenty synthetic scenarios S01–S20 (eight quiet, eight peak, four boundary).
B and T complete all twenty scenarios and satisfy every recorded hard
constraint. TM completes S01–S16 and satisfies the recorded hard constraints
on those completed scenarios; S17–S20 terminate after a negative terminal
inventory, so their logged cost (10 CNY each) covers only the executed
portion. Such a run is not a valid dispatch plan and is excluded from every
cost comparison below.

Table 1. Complete operating cost (CNY), summed within group; only
cost_complete=1 runs are included.

| Group (n) | B | T | TM |
|---|---:|---:|---:|
| quiet (8) | 800 | 760 | 640 |
| peak (8) | 800 | 760 | 1040 |
| boundary (4) | 400 | 380 | invalid (0/4 feasible) |
| Valid total | 2000 | 1900 | not definable |

On the quiet subset TM is 20% below B (640 vs 800), but on the peak subset
TM is 30% above B (1040 vs 800). Aggregated over the sixteen scenarios that
TM completes, TM costs 1680 CNY, which is 5% above B (1600) and 10.5% above
T (1520). On this scenario set the hard-constraint pass rate is 100% for B
and T and 80% (16/20) for TM. Because the scenario labels describe the
generator and no probability law is supplied, this pass rate is scenario
coverage on the fixture, not the probability of reliable deployment. No
independent held-out simulation was performed.
```

## 修订 2：替换 Discussion and conclusion 章节（整段替换原小节）

```markdown
## Discussion and conclusion
Because every hard constraint must be met before cost is considered, TM is
not eligible on this set: it is infeasible on the four boundary scenarios.
Among the eligible controllers, T is the lowest-cost choice on the recorded
fixture (1900 CNY vs 2000 for B), and T is no worse than B on every
scenario. The evidence therefore supports T over B for this synthetic
scenario set, not TM.

The paired TM-versus-T comparison isolates the effect of adding M to T:
costs fall on quiet scenarios (95 to 80) but rise on peak scenarios (95 to
130), and the four boundary runs become infeasible. The data do not support
the claim that M causes the improvement; T's own retuning already lowers
cost by 5% on every scenario, and no M-without-T variant or common tuning
budget was evaluated. M's anticipation mechanism therefore remains a
hypothesis pending a corrected selection rule (early-terminated runs are
infeasible, not ignored) and a frozen held-out evaluation. No theorem of
global optimality is claimed.
```

## 修订 3：Methods 章节保留并加一句（在原 "No M-without-T variant was executed." 之后追加）

```markdown
In addition, the TM selection score discarded early-terminated runs rather
than treating them as infeasible; under hard constraints this rule is
invalid, and any conclusions drawn from it are provisional until the
selection is repeated with a hard-feasibility gate and an independent
evaluation set.
```

## 修订影响清单（受影响的主张）
- 撤回：20% 总体节省（改为 quiet 子集描述）、90% 可靠率（改为 80%）、可靠率的概率解读、M 因果归因、"all demand conditions" 推荐。
- 新增/恢复：全 20 场景分组表、TM 完成 16 场景上的 +5%/+10.5% 对比、T 为当前可行最优（样本内）。
- 以上修订只涉及文字与表格；未改动 runs.csv，未重跑任何仿真（仿真不可得，已在 audit 标为 `unable-to-verify`）。
