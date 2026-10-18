# 根据变更安排复查

首次返回的完整论文仍须通读。此指引用于已有检查记录之后的修订；不把文件没变等同于内容正确，不跳过未解决问题，也不要求每个小任务建立依赖图。

## 先定复查范围

- 英文措辞/版式变更：核改动是否改变比较、单位、否定、因果和作用域；无需自动重算无关模型。
- 数据、代码、配置、标定或结果变化：沿依赖找到计算、图表、正文、摘要和结论，重跑相关失败检查并核重复主张。
- 用户更改目标、题意解释、约束或单位：即使所有文件哈希未变，也停止沿用旧结论，更新 brief 并重定范围。
- 问题来源、依赖图或未映射的输入变化：不能依靠旧图缩小审查；先复核范围并重建基线。

已有事实 brief、claim ledger、问题覆盖表和变更记录各保留一份，其他地方引用定位。短任务直接说明“变了什么→影响哪些结论→重查什么”。只有重复修订或依赖较复杂时才使用下列可选工具。

## 复用已有哈希缓存生成清单

为实际存在且读过的工件写 `review-map.json`，例如：

```json
{"version":1,"items":[
  {"id":"result","files":["data.csv","model.py","results.json"]},
  {"id":"figure","files":["figure.svg"],"depends_on":["result"]},
  {"id":"summary","files":["summary.md"],"depends_on":["result"]},
  {"id":"sources","files":["source-review.md"]}
],"open_items":["sources"]}
```

`files` 是直接依赖；`depends_on` 是上游检查 ID；`open_items` 保留尚未关闭的事项。图只表达人工明确声明的依赖，不能自动发现遗漏或证明审查已通过。若两个结论共用同一个大文件，文件变更会保守地影响两者；不要为了缩小范围而随意移除依赖。正文和结论的重复主张须纳入图或人工追踪。

```bash
python3 scripts/context_cache.py snapshot --root CASE --file problem.md \
  --facts brief.md --impact-map review-map.json --output CASE/context.json
python3 scripts/context_cache.py check --root CASE --manifest CASE/context.json
```

快照自动绑定图中列出的文件。`review_plan.review_items` 包含受影响项及未解决项，`unaffected_items` 仅指当前图内依赖未变，不代表验证通过。图文件、brief 或未映射输入改变会要求扩大复查；先实际完成必要检查再更新图和快照，不能仅重拍哈希把失败洗成 fresh。

口头澄清还未写入文件时，用 `check ... --context-changed`，输出必须为 stale，且不展示旧 facts；然后更新绑定 brief/上下文。新输入也须绑定。未解决事项只有实际证据支持关闭后才能移出 open_items。

## 简短记录消耗，不作虚假用量计量

结束时在已有变更记录加一句：本轮读了哪些新/改动材料、重跑哪些检查及原因、复用了哪些证据、还有什么未解决。必要时记录实际耗时。能获得准确用量才记录 token/费用；否则写“未计量”。文件数、字数、检查次数和哈希 fresh 不等于 Codex 计费额度，不换算节省比例。

所有必要复查完成且无新的影响因素时停止。证据仍不足就明确交付状态，不为得到“通过”不断换模型、润色或多代理复评。
