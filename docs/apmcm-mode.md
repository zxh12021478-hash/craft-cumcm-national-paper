# 独立 APMCM 模式

保留仓库根目录的国赛 Skill；新增技能位于 `skills/craft-apmcm-paper/`。两者拥有不同入口、规则、模板与校验脚本。

## 安装

先克隆本仓库到普通工作目录，再将完整 `skills/craft-apmcm-paper/` 目录复制到 `~/.codex/skills/craft-apmcm-paper/`。目标已存在时先备份，不要覆盖另一个国赛技能。重新打开会话后可显式调用 `$craft-apmcm-paper`。

## 使用

```text
使用 $craft-apmcm-paper，按 historical-rehearsal 模式处理附上的官方往届题。
先建立题目要求矩阵，冻结原题和解题策略，再计算、对比基线、做敏感性检验。
从实际结果写英文摘要和全文，逐项核对公式、数字、图表和英文解释。
输出可复现代码、PDF、审查记录和本地证据包；未完成项明确保留。
```

已有论文时可以仅要求英文与科学审查，不必重做整题。正式比赛前先调用规则核验流程，使用当前年度官方材料；规则未确认不会被自动填成“允许”。

## 现有资源

- [本届规则核验记录](../skills/craft-apmcm-paper/references/rules-2026.md)：包含来源、历史材料和待确认项。
- [英文工作模板](../skills/craft-apmcm-paper/assets/paper-template.md)：写作辅助，不是官方2026模板。
- [英文审查流程](../skills/craft-apmcm-paper/references/english-audit.md)：覆盖问题、语义、数据和图形。
- [证据包契约](../skills/craft-apmcm-paper/references/bundle-contract.md)：脚本执行方式与验证边界。

```bash
python3 -m unittest discover -s skills/craft-apmcm-paper/tests
```

脚本只用 Python 标准库。数字/哈希通过不代表物理模型正确、规则来源真实或能获奖。历史演练材料和用户旧提交包默认留在本地；公开技能不包含私人论文与数据。
