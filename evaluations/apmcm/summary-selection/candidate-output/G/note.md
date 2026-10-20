# G 案 note

## 关键主张定位
- Q1：瞬态只能识别 k=h/C=0.25 h⁻¹，h、C 不可分别识别（同比例缩放不变）：paper.md「Q1」段；results.json `rate_per_hour=0.25`、`transient_separately_identifies_h_C=false`；solve.py L9。
- Q2：h=50/10=5 W/K，C=h/k=20 Wh/K=72000 J/K：paper.md「Q2」段；results.json `conductance_W_per_K`、`capacitance_Wh_per_K`、`capacitance_J_per_K`；solve.py L10–L11。
- Q3：t=ln(10/4)/0.25=3.67 h > 3 h，不满足 3 小时要求：paper.md「Q3」段；results.json `time_hours=3.66516…`、`meets_3_hour_deadline=false`；solve.py L12。
- 切线外推 2.4 h 会反转达标结论：paper.md Q3 段；results.json `tangent_hours=2.4`；solve.py L13。
- 数据点已抽查（T(1)=27.788、T(2)=26.065、T(4)=23.679 与 k=0.25 解析式一致）；solve.py 复跑结果与 results.json 一致。

## 删掉了什么
- 四个瞬态原始观测值（0/1/2/4 h 全精度温度）——保留在正文 Model and data 与 data.json。
- 单位一致性说明段（Wh/K × K/h = W 等）、浮点精度说明、数据生成方式说明——正文已载。
- 两组具体不可辨识示例（h=2.5,C=10 与 h=5,C=20）压缩为一句一般机制；结论段与摘要重复的建议句删除。
- 未新增正文未报告的结果（切线 2.4 h 正文已报告，作为决策反转证据保留）。

## 未验证项 / 边界
- 数据为模型精确生成的合成输入，无测量误差模型，故无置信区间、无参数不确定性。
- 结论以给定集总模型（恒定 h、C、固定环境温度、冷却段无附加热源、温度均匀）为条件；未知热损失、空间温差、噪声、参数漂移与真实器件性能均未验证。
