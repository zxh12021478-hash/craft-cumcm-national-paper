# 三分钟上手：第一次论文审查

目标：体验一次有材料、有定位、有证据的审查。耗时是阅读与操作目标，不是模型运行时间保证；本示例没有第三方 Python 依赖。

## 1. 安装完整技能

如果尚未安装，在 macOS / Linux 的终端运行：

```bash
git clone https://github.com/zxh12021478-hash/craft-cumcm-national-paper.git \
  ~/.codex/skills/craft-cumcm-national-paper
```

Windows 或自定义技能目录用户，将完整仓库放到自己的技能目录中，并在后面的提示词中换成实际路径。已有同名目录时请先备份，不要覆盖现有修改。

## 2. 复制这段提示词

在能读取本地文件的智能体中粘贴：

```text
请读取 ~/.codex/skills/craft-cumcm-national-paper/SKILL.md，并使用该技能审查
~/.codex/skills/craft-cumcm-national-paper/examples/first-audit/ 下的
problem.md、paper-before.md 和 solver-before.py。

这是模拟审查练习。先不要读 audit-report.md、paper-after.md、verify.py
或 expected-results.json，先独立检查题意、约束、数字一致性和最优性依据。
给出每个问题的位置、证据与最小修复建议，保留原文件。
完成后，再读取参考报告并运行 verify.py 核对；说明漏检项和误报项。
```

## 3. 看结果是否有依据

参考 [审查报告](../examples/first-audit/audit-report.md)：原方案违反容量限制，论文成本与程序不一致，降本比例错误，最优性没有依据。修复后的成本是 32 元，降本约 15.79%。

不使用智能体也可以先运行演示：

```bash
cd ~/.codex/skills/craft-cumcm-national-paper
python3 examples/first-audit/verify.py
```

## 换成自己的论文

提供题目和附件、完整论文、代码入口、依赖与已有结果。可复制：

```text
使用 craft-cumcm-national-paper 审查我提供的论文和代码。
先列出已收到和缺失的材料，再优先检查核心约束、主结果、复现性及论文与代码一致性。
只报告有证据的问题；无法验证的单独列出。先给修复建议，不修改原稿。
```

仅有论文时仍可做文本与推导审查，但不能把“未发现问题”当作代码复现通过。

## 反馈

欢迎 [提交试用反馈](https://github.com/zxh12021478-hash/craft-cumcm-national-paper/issues/new?template=trial-feedback.md)。告诉我们任务类型、输入材料、实际输出和你期待的结果；不必上传未公开论文或个人信息。
