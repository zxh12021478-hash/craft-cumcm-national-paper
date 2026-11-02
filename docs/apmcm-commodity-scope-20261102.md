# 题给数据与外部统计不自动拼接

本轮沿2024 C产业联动尚缺实物/货币对应数据的缺口作有边界核对。发现的是**统计身份未对齐**，不是已证明官方题目应改成另一个数值。仅补两个现有引用，原国赛版、冻结题给数据、旧计算与PDF保持不变。

## 实际取得的证据

- 原题附件3给出2022出口24.7、2023出口39.6，单位为亿美元，未给出商品分类代码。复用已冻结的题给转录并核对原题相关内容。
- [商务部网站转载的农业贸易促进文章](https://chinawto.mofcom.gov.cn/article/jsbl/zszc/202306/20230603418510.shtml)明确讨论HS230910零售包装犬猫食品；其中2021、2022出口额分别为12.2、12.4亿美元。网页标注发布于2023-06-26，已保存快照和哈希；它是引用海关数据的官方转载文章，不冒充海关原始明细。
- 通过[UN Comtrade官方公开接口](https://uncomtrade.org/docs/un-comtrade-api/)实际取得2023年中国对世界出口HS230910的一条记录：价值1,225,836,028美元、净重266,019,000.302千克。记录保留`classificationCode=H6`、`isNetWgtEstimated=true`、`isReported=false`及`isAggregate=true`，不把估算净重称为原始实测。当前下载不是2024比赛时点的存档，不能据此声称完成实时历史回测。数量单位及估算含义分别见[单位说明](https://uncomtrade.org/docs/supplementary-quantity-units/)与[重量处理说明](https://uncomtrade.org/docs/quantity-and-weight-data-in-un-comtrade/)。

没有证明题给总额与该税目完全同范围，也没有主办方勘误。因此两组值均保留来源身份，差异继续标为未核清；不选择一个数值覆盖附件，也不由数值接近推断品类相同。

## 会改变答案的检查

按各自序列计算，题给2021至2022增幅约102.46%，文章序列约1.64%。这不是微小舍入差，但仍不能仅凭差额判断哪一列错了。不同类别、覆盖范围或资料错误均是待核解释。

同一UN记录内的贸易额除以净重约为4.608美元/千克。若把题给2023金额除以这条外部净重，会得到约14.886美元/千克，是前者约3.230倍。这个错误拼接的例子由本轮根检查主动构造，**不是实际接收者犯错**；两者量纲都成立，统计范围却尚未证明兼容。匹配记录产生的单位价值也仍受净重估算和产品组合影响，不直接等于同质成交价或价格弹性参数。

公开[来源/查询与哈希](../evaluations/apmcm/commodity-scope/source.json)、[冻结的一条API记录](../evaluations/apmcm/commodity-scope/uncomtrade-2023.json)、[检查入口](../evaluations/apmcm/commodity-scope/check.py)和[结果](../evaluations/apmcm/commodity-scope/check-results.json)。检查比对响应的年份、报告方、伙伴、流向、商品及分类字段，核算金额/重量，并确认原题转录未变。语义上的范围未核清是人工审查结论，脚本不假装能自动发现商品身份。

## 对交接与Skill的实际改进

`quick-strategy.md`现在明确：外部数据同名、同币种仍需核产品分类、期间、地区和贸易口径；与附件冲突时记录差异，保留题给数据。`task-families.md`在已有量价桥接段提醒保留估算标记，并区分贸易单位价值和同质价格。

可直接附到本案交接包的短说明：

> Preserve Attachment3 for the question-defined analysis. Keep the retrieved HS230910 series separate until its coverage is reconciled with the attachment. Do not combine the attachment's export value with the external net weight to estimate price or claim that this calibrates the full industry bridge; retain the estimated-weight flag and describe matched value/weight as an aggregate unit value.

本轮新增检查和技能结构检查通过；34份本地安装文件与源码一致。生产脚本、旧40项检查及国赛核心均未改，复用原证据。未调用付费Modex、豆包或独立AI；没有模型行为提升、额度节省或获奖概率测量。

实际接口失败分开保留：首次向单期preview接口提交两个年份返回400，按官方说明拆成单期；2022请求返回429，停止重试，未宣称取得该年UN数据；2023请求成功。未用证券研报、搜索索引或后发报告替代缺失的原始响应。

到取得明确范围对照或主办方澄清前，本轮检查到此停止。全球消费、估值及现实政策校准仍未完成，不能靠这一个外部税目补齐全部缺口。
