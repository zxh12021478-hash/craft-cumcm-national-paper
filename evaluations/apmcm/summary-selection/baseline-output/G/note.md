# G 例 note

## 关键主张定位
- Q1：仅 k = h/C = 0.25 h⁻¹ 可辨识，h、C 不可分别辨识：paper.md「Q1: identifiable rate, not separate parameters」；results.json `rate_per_hour`、`transient_separately_identifies_h_C = false`；solve.py 第 9 行。
- 等比缩放例证 (2.5,10) 与 (5,20)：同节。
- Q2：h = 50/10 = 5 W/K，C = h/k = 20 Wh/K = 72000 J/K：paper.md「Q2: independent scale information」；results.json `conductance_W_per_K`、`capacitance_Wh_per_K`、`capacitance_J_per_K`；solve.py 第 10–11 行。
- Q3：t = ln(2.5)/0.25 = 3.67 h，不满足 3 小时：paper.md「Q3: deadline decision」；results.json `time_hours`、`meets_3_hour_deadline = false`；solve.py 第 12 行。
- 切线外推 2.4 h（初速率 −2.5 K/h）会反转结论：同节；results.json `tangent_hours`。
- 合成数据边界：paper.md「Model and data」「Conclusion and limitations」；results.json `scope`。

## 删掉了什么
- 原 Summary 中四个观测点的完整浮点温度和参数的长精度数值（正文已有，data.json 保留原始精度），统一改为 0.25、5、20、72000、3.67 等正文已报告的取整值。
- 重复的模型推导表述压缩为一句解的形式。

## 未验证项
- 数据为精确模型生成的合成数据，无测量误差模型，无置信区间；未做真实器件验证（未知热损失、空间温差、噪声、参数漂移均未处理）。
- 切线 2.4 h 仅作为被否决的对照保留，不是备选结论。
- 未引入正文外的新结果或派生数字。
