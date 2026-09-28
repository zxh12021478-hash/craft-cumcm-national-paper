# 数学建模竞赛 Skill

`craft-cumcm-national-paper` 是面向全国大学生数学建模竞赛（CUMCM）的 AI 技能包，覆盖解题策略、论文与代码审查、摘要重构和提交材料打包。

以国赛一等奖水平作为质量目标，不承诺获奖。默认由另一个写作智能体完成论文正文初稿，本技能负责方向建议、证据核验和有针对性的修订。

## 主要功能

- **解题方向**：梳理题意与子问题关系，形成一份推荐解题思路大纲，包含优先方向、创新点、验证思路和备用方案。
- **论文与代码审查**：核查核心结论、可复现性、基线对比、引用和跨文件结果一致性。
- **定向修订**：保留已有合理成果，按确认的范围修复问题，并同步相关结果和图表。
- **摘要重构**：依据完整论文与已冻结结果改写摘要，支持检查正文未被修改。
- **提交准备**：提供规则核验、AI 使用披露、团队理解检查、页面检查和提交包生成工具。

## 安装

将完整仓库安装到 Codex 的技能目录，保留所有子目录：

```bash
git clone https://github.com/zxh12021478-hash/craft-cumcm-national-paper.git \
  ~/.codex/skills/craft-cumcm-national-paper
```

如果目标目录已有同名技能，请先备份，不要直接覆盖。

技能入口是 [SKILL.md](SKILL.md)。支持读取 Markdown 指令的其他智能体也可以从此文件开始，再按 `manifest.yaml` 加载所需参考资料。

## 使用示例

```text
使用 craft-cumcm-national-paper，阅读题目和附件，给我一份推荐解题思路大纲。
```

```text
使用 craft-cumcm-national-paper，审查这份完整论文、代码和结果，列出有证据支持的主要问题。
```

```text
使用 craft-cumcm-national-paper，依据完整 Markdown 论文重构摘要，其他正文保持不变。
```

## 目录

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能入口与角色边界 |
| `manifest.yaml` | 按任务加载的资料清单 |
| `agents/` | 智能体展示配置 |
| `static/` | 核心流程与阶段指令 |
| `references/` | 建模、审查、写作和评测参考 |
| `assets/` | 模板、数据结构、规则快照与离线依赖 |
| `scripts/` | 校验、审计、摘要保护和打包脚本 |
| `tests/` | 现有回归测试 |

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
