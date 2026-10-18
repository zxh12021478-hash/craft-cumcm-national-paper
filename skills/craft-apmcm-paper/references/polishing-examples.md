# Polishing Test Examples — APMCM English Paper Checks

> **Synthetic teaching material for repetitive document checking only. All sentences and numbers below are fictional. It is not, and does not quote, any official competition rule.**
> 本文件为合成教学材料，句子与数字均为虚构，仅用于重复性文档检查，不构成、不引用任何官方赛事规则。

## Global Criterion

润色通常只调整语序、连接词、词性和术语规范写法；若改动数字、单位、量纲、证据来源（assumed / rated / measured）或结论强度（best of tested / optimum、check / validation、two-point / robustness），需要有原文依据，否则判为不可接受。数字通常保留阿拉伯数字。当论文给出的具体技术定义与建议词形不同时，以具体定义为准。

---

## Example 1 — Best of tested candidates vs. global optimum

- **Original:** "We tested 4 candidate layouts, and layout B had the smallest cost, 50 dollars."
- **Acceptable:** "Of the 4 candidate layouts evaluated, layout B achieved the lowest cost, at 50 dollars."
- **Unacceptable:** "Layout B was the continuous global optimum, with the minimum cost of 50 dollars."
- **Reason:** 原文只说明在评估的 4 个候选中成本最低。若原文另行说明这 4 个候选构成离散可行域的完整枚举，可写 “the optimum over the 4-layout discrete candidate set”；在没有该说明时直接称 continuous global optimum 缺少依据。

## Example 2 — A bare residual statement stays a bare statement

- **Original:** "The normalized mass-balance residual was 0.0001 (dimensionless)."
- **Acceptable:** "The normalized mass-balance residual was dimensionless, with a value of 0.0001."
- **Unacceptable:** "The normalized mass-balance residual of 0.0001 provided experimental validation that the model was valid overall."
- **Reason:** 原句仅陈述残差的数值与量纲，合格润色只调整语序、不增删结论。不可接受版在没有独立实测数据的情况下加入了 experimental validation 和模型整体有效（valid overall）的结论，超出了原文证据。

## Example 3 — Assumed parameter follows its stated source

- **Original:** "The inlet air velocity was 2 m/s, because the problem statement did not provide it."
- **Acceptable:** "As the problem statement did not specify the inlet air velocity, it was set to 2 m/s as an assumed parameter."
- **Unacceptable:** "The inlet air velocity was measured at 2 m/s."
- **Reason:** 本例设定值的来源是题面未提供，措辞与之一致即可。实际写作中应按真实来源选择 assumed / estimated / measured，并写清来源；不可接受版无依据地把设定值改成了实测值。

## Example 4 — Units should be preserved

- **Original:** "The fan moved 300 m3/h of air."
- **Acceptable:** "The fan provided a volumetric flow rate of 300 m³/h."
- **Unacceptable:** "The fan provided a volumetric flow rate of 300 m³/s."
- **Reason:** 合格润色只规范写法（m3/h → m³/h，补全术语）。m³/h 改成 m³/s 使量大 3600 倍，属于改变单位。若原文实际是衰减试验场景，应按定义使用 CADR；本例按风机风量语境处理。

## Example 5 — Two tested points support a two-point comparison

- **Original:** "Changing parameter a from 10 to 12 changed the output from 100 to 104, a 4% change."
- **Acceptable:** "When parameter a was increased from 10 to 12, the output rose from 100 to 104, a change of 4%."
- **Unacceptable:** "Across the full range of parameter a, the output varied by at most 4%, demonstrating robustness."
- **Reason:** 原文只报告了 10 和 12 两个点的结果，支持两点比较；full range、at most 4%、robustness 超出了两点测试能够支持的范围。

## Example 6 — Nameplate rating vs. measured value

- **Original:** "The air conditioner had a cooling capacity of 3.5 kW according to its nameplate."
- **Acceptable:** "The manufacturer-rated cooling capacity of the air conditioner was 3.5 kW."
- **Unacceptable:** "The measured cooling capacity of the air conditioner was 3.5 kW."
- **Reason:** 原文数据来源是铭牌（nameplate），对应 manufacturer-rated；measured 表示实测，改变了证据来源。3.5 kW 与 kW 单位保持不变。
