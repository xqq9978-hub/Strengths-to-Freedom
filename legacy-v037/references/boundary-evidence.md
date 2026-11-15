# 收入台阶：用证据支持每一级

## 固定展示
第一台阶“本人当前收入”，第二台阶“现职责可比样本上沿”，第三台阶“新职责条件空间”。图形采用方案B，但数值顺序不保证升高；资料不足不画伪精确高度，用等高信息卡显示待核验。样本最高值不是个人硬上限，新职责范围不等于五年后保证工资。

## 需要写入的有用内容
1. 当前结构：薪资由哪些职责、固定和浮动机制决定？哪些来自本人陈述？
2. 市场参照：实际查阅的地区、行业、职责、资历、样本来源、日期、税前税后与奖金口径。目标至少2个独立可比样本，不把转载当独立来源；只有1个就明确少样本，0个保留未知。
3. 个人匹配：每个判断回到经历。列已有能力、目标职责差距、可能的反例和工具/团队依赖。不用Human3.0等级推工资。
4. 跨阶条件：任务或责任如何变化？证据门槛是什么？市场是否有真实岗位或需求？生活恢复、家庭边界和时间容量能否承受？
5. 最小验证：引用对应路径7/30/90天任务；给产物、反馈信号、继续/调整/暂停条件。不以“努力”或“多学习”代替。
6. 来源局限：报价是报价、已成交是已成交；招聘范围并非offer，名义上限不是用户可得收入。资料过时、地域不同、职责不同、变量工资未拆开都要解释。

## 数据字段
boundary_analysis={current_structure,personal_evidence_refs,current_role_range,target_role_range,gap_analysis,transition_conditions,validation_plan,path_id,limitations}。
range={low:null/number,high:null/number,status:unknown/limited/reference/estimate/simulation,unit,scope,source_refs,assumption_refs,comparability_note}。其中source_refs必须指向evidence_index内实际资料；estimate需assumption_refs；simulation仅供标明的合成演示，正式个人报告禁止使用。金额为同一unit和income_basis口径，不能从三条年曲线取最高值冒充市场上限。
gap_analysis每条为{capability,personal_evidence_refs,market_requirement,market_evidence_refs,verification_task}；其余内容用简短中文。path_id引用真实A/B/C，验证计划与该路径一致。

## 证据等级和未知
本人收入需要本人事实；市场参照需要真实访问并记录url、publisher、access_date、region、role、basis、sample_type、source_group。source_group用于区分独立来源；没有就按样本数表述，不声称独立。未实际访问不能verified=true。source_refs内verified=false或口径不匹配时不给reference标签。AI参数与测算结果显式标估计，不因“有说服力”隐藏不确定性。

## 方法参考（不是个人薪资背书）
- 国家统计局《什么是平均工资》：https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1903795.html 。说明工资统计是特定统计口径；平均值不能直接代替某个人的市场上限。
- GitLab公开薪酬方法：https://handbook.gitlab.com/handbook/total-rewards/compensation/ 。提供企业按岗位、级别、地区匹配薪酬范围的实例；不能据此证明其他地区或公司的具体金额。
以上两页于2026-11-12实际访问。只用作方法示例，不把它们登记为某个用户的岗位薪资样本，不把企业方法当作跨行业通用定律。

当前呈现以reader-report.md及odyssey-and-growth.md为准：三个主部分，台阶仅作收入部分的折叠依据；本文件的数据、引用和未知项约束保留。
