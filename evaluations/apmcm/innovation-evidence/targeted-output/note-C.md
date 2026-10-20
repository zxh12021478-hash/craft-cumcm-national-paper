# note-C：审查范围与未验证项（简短记录）

## 审查范围

- 只读输入：`input/case-C/` 下 `paper.md`、`solve.py`、`results.json` 三个原始文件，以及指定 skill；未读其他目录、旧任务输出或预期答案；未修改原材料；未联网、未调用 Modex。
- 核对动作：
  1. 重跑 `solve.py`，与 `results.json` 逐字段比对：**exact_match = True**。
  2. 独立重写枚举（itertools 全 8 子集）复核可行性与成本，结果一致：可行集仅 A+B=12、B+C=15、A+C=17、A+B+C=22；其余 4 个均因正常供给 <7 不可行；唯一最优 A+B（正常 7，失 A 剩 3、失 B 剩 4）。
  3. 核对参考方案 B+C（成本 15、正常 8、残差 3/5）与相对降幅 (15−12)/15 = 20%，计算正确。
- 结论：正文全部 headline 数字与结果文件、代码一致，状态 `verified`；summary-C.md 仅使用正文已报告结果，**未新增正文未报告的派生结果，故不产出 body-patch-C.md**。

## 未验证 / 需注意项（不影响摘要内数字，但建议处理）

1. **未见官方原题原文**：题意以 paper.md 的 Task 段为准。"Choose a subset of three available modules" 按"从 3 个模块中选子集（至多各一）"解释，最优解为 2 个模块的 A+B；若原题实际要求"恰好选 3 个"，则仅 A+B+C（22）可行，答案改变。需对照原题确认。
2. **参考方案来源与机制描述**：正文称 B+C 为"specified capacity-first reference"，但 Task 段未出现该参考；且严格按容量降序贪心（先 C 后加次大 A）应得 A+C（17），不是 B+C（15）。B+C 本身的全部数字及 20% 比较经独立核算无误；风险仅在"capacity-first/C first then B"这一构造过程描述与纯贪心不一致。建议正文改为"题定参考方案 B+C"或写明其真实构造规则。摘要已弱化为 "specified reference design"，未复述该机制。
3. 硬件可靠性、失效概率、多重失效与物理容量验证均无数据；论文 limits 已如实声明，本题为给定有限数学模型，不要求物理验证，状态 `unable-to-verify` 属预期边界。
4. 无 PDF/图表，未做渲染检查；未做哈希绑定（本测试环境无此要求）。

## 交付物

- `summary-C.md`：可直接替换的英文 Summary（仅含正式摘要内容，标题可按目标文档保留/删除）。
- `note-C.md`：本记录。
