# 数模论文审查助手

**写完数模论文后，检查模型是否满足约束、论文数字是否与代码一致、核心结论有没有证据。**

`craft-cumcm-national-paper` 是面向全国大学生数学建模竞赛（CUMCM）的 AI Skill。把题目、论文、代码和结果交给它，获得带问题位置、核验证据和修复建议的审查报告。

[三分钟上手](docs/quickstart.md) · [看审查示例](examples/first-audit/audit-report.md) · [提交试用反馈](https://github.com/zxh12021478-hash/craft-cumcm-national-paper/issues/new?template=trial-feedback.md)

## 独立 APMCM 模式

新增 [craft-apmcm-paper](skills/craft-apmcm-paper/SKILL.md)，默认快速提出可验证的解题主路线，交给 Modex 写初稿，再做公式/数字/图表与英文审查。通过按需加载、本地摘要缓存和增量审查减少重复消耗。豆包只用于制作和测试 Skill，不进入正式比赛流程。国赛入口、运行流程和校验器保持原样。

APMCM 需独立安装：[安装与使用](docs/apmcm-mode.md)。截至 2026-10-18，本届日期、语言及部分提交要求已核对；AI 政策、英文模板和详细排版规范仍待赛前公告，技能不会把历史模板当作本届规定，也不承诺奖项。

## 先看一个能自己验证的例子

一份配送方案论文声称：**满足所有约束，总成本 24 元，比基线降低 40%，达到全局最优。**

检查题目与程序后：

| 检查内容 | 发现的问题 | 修复后的结果 |
|---|---|---|
| 方案可行性 | A 仓容量只有 6，程序却分配 8 | A 发 6、B 发 4，满足需求与容量 |
| 论文与程序一致性 | 程序成本为 26，论文写成 24 | 重算可行方案成本为 32 |
| 收益计算 | 基线成本为 38，“降低 40%”不成立 | 实际降低约 15.79% |
| 最优性依据 | 原程序只返回固定方案 | 枚举全部 7 个可行方案，并给出数学证明 |

这是**有意植入错误的原创模拟案例**，不是赛事真题、真实用户评价或盲测成绩。计算已实际运行核验，输入、原程序、修订稿和检查脚本全部公开：

[题目](examples/first-audit/problem.md) → [待审论文](examples/first-audit/paper-before.md) → [原程序](examples/first-audit/solver-before.py) → [审查报告](examples/first-audit/audit-report.md) → [修订稿](examples/first-audit/paper-after.md)

## 第一次使用

### 安装

macOS / Linux 用户可在终端运行：

```bash
git clone https://github.com/zxh12021478-hash/craft-cumcm-national-paper.git \
  ~/.codex/skills/craft-cumcm-national-paper
```

保留完整目录。已有同名技能时先备份；Windows 或自定义目录的安装方式见 [上手指南](docs/quickstart.md)。

### 复制提示词

```text
使用 craft-cumcm-national-paper 审查我提供的题目、论文、代码和结果。
先检查约束、主结果和论文与代码的一致性。
请按“严重程度—位置—证据—修复建议”列出问题，并单独列出无法验证的项目。
先给报告，保留原稿，不直接修改。
```

还没有论文？按 [三分钟上手指南](docs/quickstart.md) 用随附模拟案例体验。也可以在仓库根目录直接运行：

```bash
python3 examples/first-audit/verify.py
```

演示仅需 Python 标准库。输出见 [expected-results.json](examples/first-audit/expected-results.json)，无需安装完整校验环境。

## 适合什么时候用

| 你现在的阶段 | 提供什么 | 可以要求什么 |
|---|---|---|
| 刚读完题目 | 官方题目与附件 | 一份推荐解题思路大纲，含验证方向与备用方案 |
| 已有论文初稿 | 题目、完整论文；最好同时提供代码和结果 | 证据支持的问题清单与最小修复建议 |
| 结果已确定 | 完整 Markdown 论文 | 依据正文重构摘要，保护其他内容 |
| 准备提交 | 完整论文、代码、结果与披露材料 | 规则、复现、跨文件一致性与打包检查 |

默认由写作智能体完成正文初稿，本技能负责方向建议、审查、摘要重构和定向修复。它不会因为另一种建模路线看起来更漂亮就推翻已有合理成果。

## 它能验证到什么程度？

- 有完整代码与数据时，可以尝试复现并核对核心结果；缺失材料时会列出无法验证项。
- 工具测试验证脚本行为，不等于证明模型一定能发现实际论文的所有问题。
- [历史演练记录](references/empirical-evidence-log.md) 记录了曾做过的复现工作；完整外部证据包未在本仓库分发，不作为本页的可复现演示。
- “国一水平”是原技能的质量目标，不是获奖承诺。正式提交仍由参赛团队审核确认。

## 目录导航

| 路径 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 智能体入口与角色边界 |
| [docs/quickstart.md](docs/quickstart.md) | 首次使用与自带示例 |
| `examples/first-audit/` | 可复核的微型审查案例 |
| `manifest.yaml`、`static/`、`references/` | 按任务加载的工作流程与参考资料 |
| `assets/` | 模板、规则快照、数据结构与离线依赖 |
| `scripts/`、`tests/` | 校验脚本与回归测试 |

## Python 工具与运行环境

纯指令使用不需要执行 Python。需要运行校验脚本时，可在独立环境中安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements-validator.txt
python -m unittest discover -s tests
```

`assets/runtime/wheelhouse/` 是原开发环境 macOS ARM64 / Python 3.9 的离线备份；部分 wheel 仅适用于该平台。其他系统应安装兼容依赖，并检查脚本各自的运行条件。严格环境检查会验证固定环境，不能把普通依赖安装等同于通过严格检查。

## 使用边界

- 比赛规则快照有时效性，实际参赛前必须核对当年官方要求。
- 所有数据、结果、引用与获奖相关表述都应有证据支持。
- 历史评测记录不代表对新题的独立验证；记录中 `<local-evaluation-workspace>` 指向未随仓库分发的本地评测材料。
- 正式提交仍需要真实团队确认，并遵循赛事有关 AI 使用与披露的规则。

本仓库暂未指定额外开源许可证；随附第三方依赖保留各自的许可与版权信息。
