# F 案 note

## 关键主张定位
- Q1 选 B（CNY 210，服务 95/100，最大 5.0 h）：paper.md「Base results (Q1)」表与段；results.json `base.feasible=[A,B,D,E]`、`base.chosen`；solve.py L8–L11。
- B 较参考 A（CNY 240）省 12.5%：paper.md Q1 段；results.json `base.saving_vs_A=0.125`；口径 (240−210)/240。
- C 最便宜（205）但 7.0 h 超时，不可选：paper.md 表与 Q1 段；data.json base C 行。
- Q2 仅 D 可行（CNY 255，94%，5.7 h）：paper.md「Stress results (Q2)」；results.json `stress.feasible=["D"]`、`stress.chosen`。
  - A/B/C 服务 88/84/87% 不达标；E 服务 97% 但 6.5 h 超时：paper.md 应力表与结论段。
- 场景化推荐（base→B，stress→D）：paper.md「Conclusion and limits」。
- 数字均经本地复跑 solve.py 与 results.json 一致（verified = 对所给脚本与合成表的复现，非实证验证）。

## 删掉了什么
- 两张五行完整数据表（成本/服务/时长逐行照抄）——正文两表保留，摘要只留决定选择的不可行证据。
- 单位与分母定义句（CNY、分母 100、仅对已服务请求计最大时长）——正文 Model and method 已定义。
- 应力场景各策略成本的逐行复述；原摘要末尾逐条审查清单（无置信区间/无概率/无通用推荐）合并为一句范围限定。
- 未新增任何正文未报告的数字或派生结果。

## 未验证项 / 边界
- 表为合成观测，非控制器实现或现场测量；脚本只做表筛查，不验证控制器。
- 两批次无分布联系；结论仅在五策略穷举范围内成立，不构成全局最优或未来批次保证。
- 无测量误差模型、无置信区间、无可靠性概率，未做部署实证。
