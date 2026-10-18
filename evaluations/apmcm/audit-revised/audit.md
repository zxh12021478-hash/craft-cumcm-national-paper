# 修订版独立审查（revised/audit.md，精简问题清单）

- **阶段**：非盲测修订。首轮产物（`../audit.md`、`../findings.json`、`../verify_*`）保留不覆盖；本目录仅含按 `audit-feedback.md` 四条意见修订后的产物。
- **日期**：2026-10-18；未联网、未安装、未调用付费 API；仅读反馈、授权的候选 Skill 文件（forecast-information.md、check_information.py）、audit-input 与本人首轮产物；未看其他测试目录；不评分、不代写整篇论文、不补造 Q3/Q4/Q5 结果。
- **四条修正的落实**：① 信息集规则改为 `available_at ≤ 实际预测原点`，逐 horizon 判定；② 代理在原稿已有名称 "normalized comfort objective"，补定义降级为建议；模板/覆盖表/图表源要求是 Skill 内部辅助，不计为缺陷；③ 放宽算例改用精确有理算术（残差恰为 0），并显式暴露三位小数舍入版的 −9.222×10⁻⁴ 负储能；④ 19 条按共同根因合并为 9 项，具体位置与复查保留。

## 一、问题清单（9 项；6 critical / 2 major / 1 建议；完整位置-证据-修复-复查见 findings.json）

**Q1**

- **P1（critical｜明确错误）** 百分比未由所引数值重算且混淆了代理与电能。L3 摘要"electricity…20%"：实际 100→95 kWh 仅 **5%**，20% 是无量纲舒适度代理（0.50→0.40）的降幅（也等于成本降幅）；L5 成本"25%"应为 **20%**（100→80）。已在 revised/paper.md 就地修正。复查：运行 verify_revised.py 重算三处百分比。
- **P2（建议，非缺陷）** 原稿已命名 normalized comfort objective；建议补一句"无量纲、非电能量"的定义（已补）。

**Q2**

- **P3（critical｜明确错误）** 调度不可行且约束实例本身无可行解。证据：自带/修正模型分别得 SOC [0.9,−0.9,−0.9] 与 [0.9,−1.322,−1.322]；字面约定第 2 小时仅供给 6.8<7；总量 16>15；第 2 小时上界 5.81<7；LP 两种约定均 infeasible。撤回 "feasible/globally optimal"（terminology 也不支持），并在正文显式写明题目给定的 solar=0 最差工况；正确交付是不可行证书。放宽参照（仅背景）：统一电网上限 **G*=1024/181≈5.6574586 kWh**，精确可行例 grid [1024/181,1024/181,5]、charge [300/181,0,0]、discharge [0,243/181,0]、SOC [270/181,0,0]，Fraction 精算残差为 0；三位小数舍入版 SOC=−9.222×10⁻⁴，**不得**作为 1e-6 容差可行例；放宽电池容量/充放功率无法弥补 1 kWh 总量缺口。
- **P4（major｜明确错误）** 电池方程端子约定不自洽（L7、dispatch.py L6）。已修：c 取电网侧、d 取负荷侧，E_t=E_{t−1}+0.9c_t−d_t/0.9，平衡 g+d=load+c（见 dispatch_revised.py）；原计划不可行检测如实保留，原 dispatch.py 未改。复查：量纲与往返效率 0.81 单元测试。

**Q3**

- **P5（critical｜明确错误）** 信息越过预测原点（两处同根因：L9 与 forecast.py L2）。规则：观测特征须 `available_at = source_time + 发布滞后 ≤ 原点`，逐 horizon；未知外生变量只能用原点形成的情景或删除。用 Skill 自带 check_information.py 实测：草稿 trace  tickets available_at=82、promotion available_at=83，均 > origin=80，两条 FUTURE_INFORMATION；修复 trace（工单滞后一周 79→80 恰好可用；促销改为 formed_at=80 的情景）通过。复查：对真实代码的 trace 逐原点运行，并核对 trace 与代码一致。
- **P6（critical｜明确错误）** 随机 80/20 打乱日期不能做时间外推；训练 R²=0.99 是样本内量，"99% future accuracy"撤回；out_of_sample_error=null，真实样本外评估**未执行**，不补造。修复方向：滚动/扩展起点，逐 horizon 报告误差（h=1…4 混合值不等于 h=4 误差）。

**Q4**

- **P7（critical｜明确错误）** 82/100 是分析师自选情景胜率，probability_model=null，不是真实概率（L3、L11）；要求的偏好条件排序（非支配集/权重区域/条件推荐）**未执行**。改稿保留计数、撤回概率与唯一赢家、"optimal"。

**Q5 / 结论**

- **P8（critical｜明确错误）** Q5 整问缺失（无正文、无结果、无代码）；L13 "All requested questions have been fully answered" 为假。改稿把 Q5 标为 not executed（±5% 双方向、反转与后悔值待修复后运行），结论改为逐问状态清单。

**贯穿**

- **P9（major｜无法验证）** Q2 无求解模型/运行日志、Q3 仅伪代码无数据入口种子、Q4 无情景构造、Q5 无任何产物——状态保留 unable-to-verify。覆盖表、模板章节、图表源属于 Skill 内部辅助，本题未要求图表，不作为缺陷提出。

## 二、保留的正确内容（C01–C07）

25 °C 温度目标（L3、L13）；舒适度代理 0.50→0.40；电能 100→95 kWh；成本 100→80 CNY；grid [5,5,5] 与充放功率逐时分量满足 ≤5、≤2 且初始储能为零；训练 R²=0.99 作为样本内记录值；82/100 作为计数本身。（错误的只是它们的百分比表述/概率解释与所声明的可行性，均已在 P1/P3/P6/P7 处理。）

## 三、未解决项（不包装成可提交终稿）

1. Q2：需题方接受某项约束放宽后才有可行方案（放宽参照已给，决策不属审查）。
2. Q3：原点合规特征集与滚动起点的逐 horizon 样本外误差——未执行。
3. Q4：支配筛选、权重区域、条件推荐——未执行。
4. Q5：±5% 双方向敏感性、排序反转与后悔值——未执行。

## 四、复核方法

```bash
cd independent-audit/revised
python3 dispatch_revised.py   # 原计划违例；精确放宽例残差 0；舍入版 −9.222e-4
python3 verify_revised.py     # Q1 重算；Q2 LP 与精确值；Q3 原点守卫；Q4/Q5 结构
```

关键输出：verify_output.txt（两脚本原始输出）、information-audit.json（原点守卫记录）、verify_results.json。最小改稿见 paper.md（含变更说明，非完整论文）。
