# Task B — paper.md 实质审查（audit-B.md）

## 核查范围
- 输入：仅 paper.md 与 results.json（本微型案声明无 PDF、代码、实验数据、电表、当届官方模板）。
- 已执行：probe_B.py（标准库）→ probe_B_result.json；未联网、未安装、未运行模拟。
- 顺序：先答案级错误与证据问题，再语言/版面；A、B 证据不混用。
- 总体判断：正文 Q1–Q3 的叙述（paper.md 第 6–13 行）基本克制且与结果一致；**Summary（第 3 行）包含三处答案级错误并与正文自相矛盾**，须整体替换（替换稿见 summary-B.md）。无需改模型。

## 一、答案级发现（answer-changing）

### F1　“100% 一致 + 实验验证”为伪
- 位置：Summary 第 1 句 “A perfect 100% agreement with commercial CFD experimentally validates our model.”
- 证据：results.json Q1：model [[10,20],[10,20]] 与 CFD [[20,10],[20,10]] 在 4 个匹配单元上数值全部互换；probe_B 结果：一致率 **0/4**、MAE=RMSE=**10 °C**、逐元相关 **−1**；range_overlap=1 只反映全局范围相同（两场均值同为 15 °C、范围同为 [10,20]）。paper.md 第 7 行自述“必须在匹配单元比较后才能声称空间一致”，且“CFD 场不是测量参考”；第 5 行声明无实验。
- 后果：一句内含三重错误（一致率、实验验证、把 CFD 当测量基准）。
- 修复：改为匹配单元指标（0/4 一致、MAE/RMSE 10 °C、相关 −1）；明确仅为 code-to-code 比较，删除 experimentally validates。
- 复查：probe_B_result.json → Q1_matched_cell；summary-B.md 对应数字。

### F2　确定性参数区间被误称为“95% 置信区间”，且它证明的是“不稳”而非“稳定”
- 位置：Summary 第 2 句 “The 95% confidence interval [0.95p,1.05p] proves stability.”
- 证据：results.json Q3 multiplier=[0.95,1.05]、probability_model=**null**；paper.md 第 11 行：确定性扰动，非统计置信区间，无概率或重复抽样；上端点 1.05p0 时 H=105 > J=92，**推荐发生反转**。
- 后果：区间性质误标；证据实际显示决策对参数敏感（排序反转），与“stability”相反。
- 修复：改称 deterministic parameter range；写明上端点 J 优于 H、推荐为条件性结论。
- 复查：probe_B_result.json → Q3_check。

### F3　“普适最优 H 减少实际用电 20%”为伪
- 位置：Summary 第 3 句 “Our universally optimal heater design H reduces actual electricity use by 20%.”
- 证据：Q2 仅在两个受测策略、基参数 p 下 H(80)<J(90)<baseline(100)；Q3 上端点 J 更优（中间与外部工况未测）；paper.md 第 9 行明确“代理分数不是电能或成本”，第 5 行声明无电表；0.2 = (100−80)/100 是**代理分数**的相对降幅（probe_B 复算一致）。
- 后果：① 有限受测集 + 场景受限被夸成 universally optimal；② 代理指标被当成实际电量；③ 20% 的单位与对象错误。
- 修复：改为“基设置下 H 在两个受测策略中模拟不适代理最低（相对基线代理降 20%）；不代表电能”。
- 复查：probe_B_result.json → Q2_check。

## 二、证据范围与方法缺口

### F4　Q1 只给了范围重叠，未报告匹配单元空间指标
- 位置：paper.md 第 7 行（只报 range-overlap=1）。
- 后果：范围相同但空间完全相反（相关 −1），单凭范围重叠会导致错误结论。
- 修复：补 0/4 一致率、MAE/RMSE 10 °C、相关 −1；范围重叠仅保留为描述性标志，二者分列。
- 复查：probe_B_result.json Q1 段。

### F5　Q3 只测了上端点，覆盖不完整
- 位置：paper.md 第 11 行；results.json 无下端点分数。
- 后果：不能声称整个 [0.95p0,1.05p0] 上稳健；下端点、中间参数、外部工况均无证据。
- 修复：明确列出未测项；结论限定为“基设置选 H，已测上端点选 J”。
- 复查：audit-B “未核查项”清单。

### F6（正向记录）正文结论与结果一致，问题集中在 Summary
- paper.md 第 12–13 行结论已正确区分空间比较、物理验证与区间解释，并给出条件性推荐。
- 处理：以正文为准重构 Summary；无需模型或数值改动，属措辞/证据范围修复。

## 三、未核查项（单列）
1. 可执行代码、PDF、实验数据集、电表读数：均未提供（paper.md 声明不存在）→ 经验验证、求解正确性、可复现性均无法核查。
2. 下端点 0.95p0 的策略分数：未提供。
3. 中间参数取值下的结果：未测试。
4. 外部运行条件：未测试。
5. 代理分数 → 实际电量的映射：无模型、无标定，任何电量/节能结论均不可得。
6. CFD 结果的来源与质量：与模型共享假设边界条件、非测量参考，仅按给定数据接受。
7. 当届官方规则/模板/版面与评分：不在本次范围，材料亦声明无当届模板。
8. 核查边界仅限 paper.md + results.json 与 probe_B 计算；未使用任何其他来源或 Task A 的证据。

## 四、修复性质与停止条件
- F1–F3、F5：措辞与证据范围修复（不新增计算，所需指标已由 probe_B 从现有数据算出）。
- F4：补入由现有数据计算的匹配单元指标（probe_B）。
- 替换 Summary 已交付（summary-B.md）；未改模型、未重跑模拟；问题关闭条件为替换稿中每个数字与 probe_B_result.json 一致，且不出现 confidence interval / experimentally / electricity / universally optimal 等超范围表述。
