# GitHub 数模 Skill 学习与选择性融入（2026-10-18）

本次直接使用 GitHub 连接器检索仓库、读取真实文件并固定提交；不是仅凭 README、Star 或“获奖”宣传筛选。目标保持：APMCM Skill 生成 Modex 交接包，Modex 实现并写初稿，Skill 审查修改。豆包仅在制作阶段做资料去重与独立试用，不进入比赛。

## 值得参考的来源

Star 是检索时快照，仅帮助发现项目，不是效果证据。仓库/文件固定提交、Blob哈希和许可见 [来源记录](../evaluations/apmcm/github-learning/sources.json)。

| 项目 | 当次 Star 快照 | 阅读后采用或保留的价值 | 未沿用的部分 |
|---|---:|---|---|
| [MathModelAgent](https://github.com/jihe520/MathModelAgent/blob/03f4eb388b3862b7bde55b508dceaf3d6b39d5ac/skills/2analysis-modeling/SKILL.md) | 6,220 | 影响答案的歧义先做假设预检；公式需足够直接实现 | 不把“后问失去边际效果”直接当作改题意的理由；不替代 Modex 的主笔角色；未检出顶层许可，不复制原文/代码 |
| [MathModel-Skill](https://github.com/yushui2022/MathModel-Skill/blob/286643e9bea39922297f4d46314a5f6d05b924cd/packages/codex/.agents/skills/model-code-and-result-generator/references/modeling-tools.md) | 457 | 独立重算线性约束、显式边界、整数性与原目标；可行性不等于最优性 | 不导入整个 S0–S8 写作系统、默认字数/页数、重型依赖；以标准库重新实现所需核查 |
| [路线选择 Skill](https://github.com/y3519712124-ui/math-modeling-contest-route-selection/blob/bb15e079e6e4566cde3d0868fef0609681ef0594/math-modeling-contest-route-selection/references/refutation-and-model-choice.md) | 91 | 最强反驳、决定性小检查、可复用 fallback 和实际时间预算 | 不默认每题展开多路线锦标赛，不使用任意主观分差作确定排名，不套国赛评分规则 |
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/pymoo/SKILL.md) | 52,404 | 可行点先筛；随机算法匹配目标评价预算/种子；多目标统一方向、缩放、参考点。另参考 [idea evaluation](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-brainstorming/references/idea_evaluation.md) 的硬否决项不能被平均分掩盖 | 不默认 NSGA、安装整库或把未给概率的权重采样当实证；不强制论文写作代理 |
| [Context Engineering Skills](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/9ff0c99108b36d3b886defd825d8ac1f47dba374/skills/context-optimization/SKILL.md) | 18,159 | 已解决长输出外置、保留证据指针；当前决定与未解决反证进入精简状态 | 不采用未经本机测量的节省比例、上下文百分比阈值、多代理拆分或服务端缓存折扣假设 |
| [XiaoMaColtAI math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill/blob/05011685611ce25452e44da0407b83bec5366ebe/references/交付与截止时间协议.md) | 1,876 | 当前最好可用版本应先保全，后续优化不能破坏基线；现有复现/哈希流程继续保留 | 固定图数、页数、默认多代理质检及全文流水线不符合本项目范围；未检出顶层许可，不复制原文/代码 |

另查看 Google DeepMind science-skills 的介绍，其当前主线以专门科学数据/工具任务为主，没有仅因品牌而加入本数模工作流。

## 已融入的位置

- `references/route-challenge.md`：题面证据、两种影响答案的解释、一次最强反驳、停止/备用条件，以及不能为增加复杂度改题意。
- `references/solver-review.md`：可行/最优证据边界、公平对照与前沿指标口径；交接阶段只安排必要计划，不先完整解题。
- `scripts/check_linear_solution.py`：新写的标准库独立复核器。检查原始线性部分、边界、整数性和目标值，拒绝错误符号和无效数值；始终不证明最优。
- 快速指引与交接模板只加必要路由和字段；不默认加载来源仓库或全部新参考。保留现有缓存，并补充未解决失败信息不能被压缩丢弃。

原国赛核心保持原样。外部材料只作为研究对象，不执行其安装、权限、审批或多代理指令；许可与致谢见 [上游方法说明](upstream-method-notices.md)。

## 验证

APMCM 脚本测试从22项增至30项，新增约束违例、最优化符号、负自由变量、大数整数性、非有限/维度错误、非最优可行解等测试。通过不意味着整题建模质量或获奖保证。

另用新的原创短题检查“新增价格未改变满载调度时，不得强凑创新”，以及三份线性候选的可行性/目标口径。独立穷举17个可行整数点得到最优23；复核器拒绝违约候选，接受可行但非最优候选的约束检查，同时拒绝把最大化目标23误报成−23。详情见 [独立检查](../evaluations/apmcm/github-learning/root-checks.json)。

豆包提出8条建议，主代理逐条裁定；其中“后问条件无边际作用就必须改解释”等过强规则未采纳。正向试用正确保留满载调度，三份候选的实际审计与独立穷举一致；仍发现一处不等式笔误、一般可行条件不完整和交接过长，已另存主代理修订版（原稿保留）。见 [试用验收](../evaluations/apmcm/github-learning/forward-assessment.json) 和 [精简交接示例](../evaluations/apmcm/github-learning/root-reviewed/handoff.md)。没有把这一次开发试用当作广泛效果证明或额度节省计量。真实 Modex 完整往返、完整官方题的冻结盲测、实际 Codex 用量对照仍是单独的验证工作；本次不声称这些已经通过。
