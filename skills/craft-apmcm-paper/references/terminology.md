# Terminology Reference — APMCM English Paper Checks

> **Synthetic teaching material for repetitive document checking only. It is not, and does not quote, any official competition rule.**
> 本文件为合成教学材料，仅用于重复性文档检查，不构成、不引用任何官方赛事规则。

## Usage

- 全文术语首次出现写“全称 + 缩写”，之后统一用缩写。
- 本表给出的是建议词形与常见技术定义，**不是词语黑名单**；同一概念在不同文献中常有多种写法，检查时以论文给出的具体技术定义、单位和推导为准：具体技术定义优先于建议词形。
- 检查重点：术语全文是否统一、单位与量纲是否匹配、结论强度是否与证据一致。

| # | 中文 | 建议英文 | 单位 | 定义与用法说明 |
|---|---|---|---|---|
| 1 | 体积流量 | **volumetric flow rate**（volume flow rate 同样常见） | m³/s, m³/h | 单位时间流过的体积。写作 volume flow rate、volume flow 在不同教材中都可遇到，建议全文统一一种；flux 通常指面积归一化的通量（m/s），定义不同，不宜与流量互换。 |
| 2 | 风速 | **air velocity**（室内、风道、设备进出口）；**wind speed**（室外气象） | m/s | 按场景选择：室内 HVAC 与风道常用 air velocity；室外风环境常用 wind speed。 |
| 3 | 电输入功率 | **electrical input power** | W, kW | 指瞬时功率。为避免歧义，建议直接写 electrical input power (W) 与 electrical energy (kWh)。power consumption 在行业文献中也常用来表示耗电功率（W），并非只限电能（Wh）；以实际单位和句子定义为准。 |
| 4 | 制冷量 | **cooling capacity** | W, kW | 空调样本与标准中的常用术语。cooling power 等写法在部分文献中也可见，若全文已定义且单位一致即可，不必强行替换。 |
| 5 | 相对湿度 | **relative humidity (RH)** | %（无量纲） | 空气中水蒸气分压与同温度饱和分压之比。RH 是无量纲百分数；与 humidity ratio 是不同定义，同篇出现时分别说明即可。 |
| 6 | 含湿比 | **humidity ratio** | kg/kg dry air | 通常定义为水蒸气质量 / 干空气质量。specific humidity 可共存，定义为水蒸气质量 / 湿空气总质量；两者同现时建议在首次出现处写明分母，全文按各自定义一致使用。 |
| 7 | 颗粒物浓度 | **particle concentration**；质量浓度 **mass concentration**，数浓度 **number concentration** | μg/m³；#/m³ | particle concentration 可指质量浓度或数浓度，建议在文中明确是哪一种；本案例 μg/m³ 对应的是质量浓度。density 是密度，与浓度概念不同，但是否同单位取决于具体量纲，不宜一概而论。 |
| 8 | 洁净空气量 | **clean air delivery rate (CADR)** | m³/h | 通常由颗粒物衰减试验得到的等效洁净空气输送率，定义与风机 volumetric flow rate 不同；引用时建议同时说明测试方法与工况。 |
| 9 | 基线 | **baseline** | — | 通常指自有对照方案及其结果。benchmark 不必来自外部：文献值、标准工况或自定义参照点都可以；按研究中实际承担的角色区分即可。 |
| 10 | 消融实验 | **ablation study** | — | 建模与机器学习文献常用说法；若所属领域已有惯用表达（如 component removal analysis），按领域惯例统一即可。 |
| 11 | 敏感性分析 | **sensitivity analysis** | — | 按实际分析范围描述：单参数、单组扰动可以是敏感性分析的一部分，也可单独成文；建议写清扰动范围、取值与响应指标，结论不超出实际分析即可。 |
| 12 | 有限候选中的最佳方案 | **best of the candidates tested / best among the evaluated alternatives** | — | 未说明完整枚举时建议带 tested 限定；若有限可行域被完整枚举，可称该离散域最优，写 “the optimum over the discrete candidate set”；向连续域或未评估构型外推时需要额外的最优性论证。 |
| 13 | 全局最优 | **global optimum / globally optimal solution** | — | 连续语境下使用通常需要凸性、最优性条件或可证界支撑；来自离散枚举的结论建议限定在该离散域内。 |
| 14 | 数值守恒残差 | **conservation residual**（mass-balance / energy-balance residual）；归一化写 **normalized ... residual** | kg/s、W，或无量纲 | 残差小通常说明收支闭合良好。是否称 error 取决于是否有真值对照；残差小本身不构成模型整体有效的充分证据。 |
| 15 | 实验验证 | **experimental validation** | — | 通常指有独立实测数据对照的验证；若依据仅是数值残差、重算或内部核对，建议用 numerical check / internal consistency 等更贴切的表述。 |
| 16 | 假设参数 | **assumed parameter** | 随量 | 用于由作者设定、缺乏直接来源的参数。理由应按真实来源写（题面未提供、超出文献范围、待标定等），不规定统一措辞；若存在估计过程用 estimated，有实测数据用 measured。 |
| 17 | 厂商标称参数 | **manufacturer-rated parameter / nameplate value** | 随量 | 来自厂商铭牌或样本的额定值，与实测值 measured value 是不同来源。nominal 在不同语境另有含义（如名义量），首次出现建议写全称并给出定义。 |

## Quick Rules

- **W vs Wh**：建议直接命名 electrical input power (W) 与 electrical energy (kWh)；以单位和句子定义为准。
- **best vs optimum**：完整枚举有限离散域时可称该域 optimum；连续域全局最优通常需要最优性证明；未证明完整枚举时用 best of tested 更稳妥。
- **residual vs validation**：残差小通常支持收支闭合的表述；独立实测数据对照才适合称 experimental validation。
- 以上均为建议；当论文给出的具体技术定义与建议词形不同时，以具体定义为准，并保证全文统一。
