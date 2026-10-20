# 独立读者回读记录（readback）

- 范围：仅依据 reader-input 内 request.md、R1–R4 的 question.md 与 summary.md 回读；未读取包外任何材料，未联网，未据题面补算。
- 体例：每问列出摘要明说的答案/机制/比较/范围，括注为摘要原文短定位（英文原文照引）。摘要未明说处标"摘要未说明"。
- 说明：所有数值在输入包内仅出现于 summary.md（题面不含数据表），以下只做恢复，不复核、不打分。

---

## R1 集总冷却模型

**模型/机制**
- 解为 T(t) = Ta + (T0 − Ta) exp(−kt)，k = h/C。定位："the solution is T(t) = ... exp(−kt), where k = h/C"。

**Q1（瞬态实验单独可识别什么）**
- 只能识别比值 k = 0.25 h⁻¹；h、C 不可分离。定位："give k = 0.25 h⁻¹, but the transient alone identifies only this ratio"。
- 机制：h 与 C 同乘任意正倍数不改变 k 与温度预测。定位："any common positive rescaling of h and C leaves k and the predicted temperatures unchanged"。

**Q2（结合稳态加热实验）**
- h = 5 W/K，C = 20 Wh/K。定位："50 W input, 10 K equilibrium rise ... giving h = 5 W/K and C = 20 Wh/K"。

**Q3（30→24 °C，环境 20 °C，是否满足 3 小时）**
- 耗时 3.67 h，3 小时要求不满足。定位："takes 3.67 h, so the 3-hour requirement is not met"。
- 对照：按初始冷却率作一阶切线得 2.4 h，会反转结论，因为接近环境温度时速率递减。定位："a first-order tangent ... would give 2.4 h and reverse the decision by ignoring the declining rate"。

**范围/限制**
- 规定集总模型 + 合成数据 + 无测量不确定度下的精确结果；不是物理参数测量、置信区间或真实器件性能证据。定位："exact results for the stipulated lumped model with synthetic data and no measurement uncertainty"。

**歧义/缺口**
- 摘要未说明 k=0.25 由何种观测或拟合得到；未单列 h、C 的推导式。

---

## R2 加权排序与鲁棒区间

**机制**
- S = w·criterion1 + (1−w)·criterion2；S_X = 3 + 6w，S_Y = 8 − 2w。定位："S_X = 3 + 6w and S_Y = 8 − 2w"。

**Q1（w=0.4）**
- 分数：X 5.4、Y 7.2、Z 3.2；Y 唯一胜出。定位："X 5.4, Y 7.2 and Z 3.2, so Y is the unique winner"。

**Q2（w 未知时的胜者与平局）**
- Y 胜：0 ≤ w < 5/8；w = 5/8 时 X、Y 平局；X 胜：5/8 < w ≤ 1；Z 被 X 严格占优、从不获胜。定位："Y wins for 0 ≤ w < 5/8, X and Y tie at w = 5/8 ... Z is strictly dominated by X"。

**Q3（X1∈[8,10]、Y1∈[5,7] 独立扰动下的保证区间）**
- S_X − S_Y 取值范围为 [6w − 5, 10w − 5]。定位："S_X − S_Y ranges over [6w − 5, 10w − 5]"。
- Y 保证不劣于所有对手：0 ≤ w ≤ 1/2；X 保证不劣于所有对手：5/6 ≤ w ≤ 1。定位："Y is guaranteed no worse ... for 0 ≤ w ≤ 1/2 and X for 5/6 ≤ w ≤ 1"。
- 端点为弱保证：极端扰动可逼平。定位："at the boundary an extreme perturbation can force a tie, so both are weak guarantees"（摘要未明说"the boundary"是单指一个端点还是 w=1/2 与 5/6 两个端点）。
- 1/2 < w < 5/6：胜者取决于实现值，仅支持条件选择；Z 全程被占优。定位："only a conditional choice is justified, and Z remains dominated throughout"。

**范围/限制**
- 有界不确定集上的精确解析区域，不是概率、置信区间或可靠性结论。定位："exact analytic regions over a bounded uncertainty set, not probabilities, confidence intervals, or reliability claims"。

**歧义/缺口**
- 摘要未给出 S_Z 的表达式；保证"不劣于所有对手"的论证只展示了 S_X−S_Y 区间，未展示对 Z 的比较区间。

---

## R3 五个固定派单策略选择

**机制/判据**
- 先可行性后成本：至少服务 90% 请求、已服务请求最大送达时间 ≤ 6 h，之后才比较完整成本。定位："applying feasibility first—at least 90% ... at most 6 hours ... comparing complete cost only afterward"。

**Q1（基础批，100 请求）**
- B 为成本最低可行方案，CNY 210；比参照 A（CNY 240）便宜 12.5%。定位："B is the least-cost feasible policy at CNY 210, 12.5% cheaper than the reference A at CNY 240"。
- C 成本更低（CNY 205）但最大送达 7.0 h 超时，被排除。定位："C is cheaper at CNY 205 but is excluded because its 7.0 h maximum violates the time limit"。

**Q2（压力批，情景化建议）**
- B 不合格：仅 84% 获服务；D 是唯一可行策略，成本 CNY 255。定位："B fails with only 84% served and D is the only feasible policy at CNY 255"。
- 建议：基础批用 B，压力批用 D。定位："B for the base batch and D for the stress batch"。

**范围/限制**
- 仅覆盖所测五个策略与所给合成表；不主张在所有可能策略中最优、不保证未来批次、不代表真实部署；表格是合成观测而非经验证的模拟器。定位："exact results over the five tested policies and the supplied synthetic tables ... not evidence that B or D is optimal among all possible policies"。

**歧义/缺口**
- 摘要称两批均为 100 请求（"two batches of 100 requests"），但题面 Q2 未写压力批数量；
- D 在压力批的服务率与最大时长、A/E 等其余策略在两批的可行性与成本、基础批 A 的服务率/时长，摘要均未说明。

---

## R4 模块子集选择（回归控制）

**机制/判据**
- 枚举三个模块的全部 8 个子集，最小化安装成本；约束：正常供给 ≥ 7 units/day；任一已装模块失效后剩余供给 ≥ 3 units/day；模块不可分、容量无损相加。定位："enumerate all eight subsets ... normal supply of at least 7 ... remaining supply of at least 3 after any single installed-module failure"。

**Q1（选子集）**
- 唯一最优：A+B，成本 CNY 12；比"定义的参照设计 B+C"（CNY 15）低 20%。定位："The unique optimum is A+B at CNY 12, 20% below the defined reference design B+C at CNY 15"。

**Q2（所选设计各单模块失效后的剩余供给）**
- 失 A → B 供 3 units/day；失 B → A 供 4 units/day；均满足 ≥3。定位："losing A leaves B supplying 3 units/day and losing B leaves A supplying 4 units/day, both meeting the required 3"。

**范围/限制**
- 加法容量模型与规定意外集下的精确有限枚举证明；不确立硬件可靠性、失效概率或未指明多重失效下的表现。定位："an exact finite-enumeration certificate under the stated additive-capacity model and contingency set"。

**歧义/缺口**
- "reference design B+C at CNY 15"未在本组 question.md 中出现，包内仅见于摘要，无法定位其依据；
- 各模块单价/容量摘要未单列（仅由残量知 B=3、A=4；A+B 正常总供给 7 units/day 属简单推算，摘要未直接写出）；
- 其余 6 个子集被排除的具体原因（成本或违反项）摘要未说明；第三个模块名称 C 仅在参照设计中出现。

---

## 跨组观察

- 四份摘要均自带与题面一致的"合成数据/精确结果/禁止外推"范围声明；
- 所有数值在输入包内仅有摘要一个来源，本次未做独立复核，也未发现摘要之间相互引用；
- 未发现必须借助包外材料才能理解的内容。
