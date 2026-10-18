# 独立 APMCM 模式

保留仓库根目录的国赛 Skill；新增技能位于 `skills/craft-apmcm-paper/`。两者拥有不同入口、规则、模板与校验脚本。

## 安装

先克隆本仓库到普通工作目录，再将完整 `skills/craft-apmcm-paper/` 目录复制到 `~/.codex/skills/craft-apmcm-paper/`。目标已存在时先备份，不要覆盖另一个国赛技能。重新打开会话后可显式调用 `$craft-apmcm-paper`。

## 使用

```text
使用 $craft-apmcm-paper 的快速思路模式处理这道题。
给一条推荐主路线、关键公式、可验证创新、最小验证方案和备用路线触发条件。
按需读取并复用已核对材料，只做路线选择必需的少量检查。
先输出 Modex 交接包并等待；Modex 实现、计算并写全文初稿，收到论文、代码与结果后再审查修改。
```

正式比赛沿用国赛的两阶段分工：Skill 生成交接包 → Modex 初稿 → Skill 审查修改。豆包仅用于制作和测试 Skill，不是比赛依赖。默认先产出策略，不自动完整解题或撰写全文，也不要求先完成全部验证才能交接。需要完整往届题演练或深度物理验证时明确提出，或由已确认的重大风险触发。

交接前按需检查预测信息泄漏、未知偏好、优化可行性或机理可辨识性；不固定套用某类模型。收到初稿后先处理改变答案的错误，再处理证据和英文；后续版本只复查变化及影响。复杂题保留原题要求矩阵，防止审稿时整问遗漏。

已有论文时可以仅要求英文与科学审查，不必重做整题。正式比赛前先调用规则核验流程，使用当前年度官方材料；规则未确认不会被自动填成“允许”。

## 开发验收

见 [跨题型与审查测试协议](../evaluations/apmcm/protocol.md)。[本轮实际结果与未完成项](../evaluations/apmcm/results-20261018.md)单独记录。测试答案不进入比赛上下文；合成测试通过不能代替真实 Modex 往返、完整往届题盲测或实际额度计量。

## 现有资源

- [本届规则核验记录](../skills/craft-apmcm-paper/references/rules-2026.md)：包含来源、历史材料和待确认项。
- [英文工作模板](../skills/craft-apmcm-paper/assets/paper-template.md)：写作辅助，不是官方2026模板。
- [英文审查流程](../skills/craft-apmcm-paper/references/english-audit.md)：覆盖问题、语义、数据和图形。
- [证据包契约](../skills/craft-apmcm-paper/references/bundle-contract.md)：脚本执行方式与验证边界。

```bash
python3 -m unittest discover -s skills/craft-apmcm-paper/tests
```

脚本只用 Python 标准库。数字/哈希通过不代表物理模型正确、规则来源真实或能获奖。历史演练材料和用户旧提交包默认留在本地；公开技能不包含私人论文与数据。
