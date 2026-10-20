# 修订版读者回读（revision-readback）

- 范围：仅依据 reader-revision-input 内 request.md、R1/R2 的 question.md 与 summary.md 回读；未看全文/结果/作者note/预期答案，未据题面补算、未联网、未打分。
- 两份 question.md 与前次输入包中对应题面文本一致。
- 结论先行：**两组数值答案与前次记录完全一致，无任何数值差异**；仅有两处措辞修订（见各组"与前次差异"）。

---

## R1 集总冷却模型

**机制**：T(t) = Ta + (T0 − Ta) exp(−kt)，k = h/C。定位："where k = h/C"。

- **Q1**：瞬态实验仅识别 k = 0.25 h⁻¹；h、C 不可分离（共同正倍数缩放不改变 k 与温度预测）。定位："give k = 0.25 h⁻¹, but the transient alone identifies only this ratio ... any common positive rescaling"。
- **Q2**：h = 5 W/K，C = 20 Wh/K（50 W 输入、10 K 平衡温升提供尺度）。定位："supplies the missing scale, giving h = 5 W/K and C = 20 Wh/K"。
- **Q3**：30 → 24 °C（环境 20 °C）耗时 3.67 h，3 小时要求不满足；初始速率一阶切线得 2.4 h 并会反转结论。定位："takes 3.67 h, so the 3-hour requirement is not met; a first-order tangent ... would give 2.4 h and reverse the decision"。

**范围限定**：规定集总模型 + 合成数据下的精确结果，**无给定的测量误差模型**；不是物理参数测量、置信区间或真实器件性能证据。定位："exact results for the stipulated lumped model with synthetic data and no supplied measurement-error model"。

**与前次差异**：数值无变化。范围措辞由前次的 "no measurement uncertainty" 改为 "no supplied measurement-error model"（含义从"无测量不确定度"变为"未提供测量误差模型"）。

---

## R2 加权排序与鲁棒区间

**机制**：S = w·criterion1 + (1−w)·criterion2；S_X = 3 + 6w，S_Y = 8 − 2w。定位："S_X = 3 + 6w and S_Y = 8 − 2w"。

- **Q1（w=0.4）**：X 5.4、Y 7.2、Z 3.2，Y 唯一胜出。定位："X 5.4, Y 7.2 and Z 3.2, so Y is the unique winner"。
- **Q2（平局边界）**：Y 胜 0 ≤ w < 5/8；w = 5/8 时 X、Y 平局；X 胜 5/8 < w ≤ 1；Z 被 X 严格占优、从不获胜。定位："Y wins for 0 ≤ w < 5/8, X and Y tie at w = 5/8"。
- **Q3（弱保证边界）**：S_X − S_Y ∈ [6w − 5, 10w − 5]；Y 保证不劣于所有对手 0 ≤ w ≤ 1/2，X 保证不劣于所有对手 5/6 ≤ w ≤ 1；**在 w = 1/2 或 w = 5/6 处，极端扰动均可逼平，故两者均为弱保证**。定位："at w = 1/2 or w = 5/6 an extreme perturbation can force a tie, so both are weak guarantees"。1/2 < w < 5/6 仅条件选择；Z 全程被占优。

**范围限定**：有界不确定集上的精确解析区域，不是概率、置信区间或可靠性结论。定位："exact analytic regions over a bounded uncertainty set, not probabilities, confidence intervals, or reliability claims"。

**与前次差异**：数值与区间无变化。弱保证边界的表述由前次含糊的 "at the boundary an extreme perturbation can force a tie" 明确为 "at w = 1/2 or w = 5/6"，即两个端点均为弱保证——前次记录中标注的该处歧义已消除。

---

## 汇总

- 数值差异：无（R1：k=0.25 h⁻¹、h=5 W/K、C=20 Wh/K、3.67 h、2.4 h；R2：5.4/7.2/3.2、5/8、1/2、5/6、[6w−5, 10w−5]，均与前次一致）。
- 措辞差异：R1 范围限定改为"无给定测量误差模型"；R2 弱保证端点明确为 w=1/2 与 w=5/6 两个。
- 残留缺口同前：R1 未给 k 的拟合方式；R2 未给 S_Z 表达式及对 Z 的保证区间。
