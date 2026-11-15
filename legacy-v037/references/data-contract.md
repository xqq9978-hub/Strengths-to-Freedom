# 统一报告数据契约 v0.3.7

以report.json为唯一事实与分析数据包；reports只保存三个部分的引用和同一revision，不复制三份事实。JSON Schema见report.schema.json；可运行校验见scripts/validate_report.py。结构校验只能检查已编码规则，不能证明证据真实或理论有效。

## 来源与数值
Claim统一为 {kind,value,evidence_refs,assumption_refs,unknown_refs}；kind为fact/market_reference/inference/assumption/unknown。unknown值为null并有unknown_refs；事实、推断和市场参考必须有可追溯证据；假设必须有assumption_refs。列表空表示没有条目，不代表用户“没有能力”。证据记录source_type、turn、quote、status、verified、url、publisher、access_date、region、role、basis；用户自述不等于外部验证。
assumptions记录id、description、accepted(true/false/null)、reason、failure_condition。外部资料仅真实查阅后verified=true并补来源信息；无法联网使用unknown，不捏造URL。个人收入敏感可拒答。

## 顶层字段
- schema_version、report_id、revision、state：会话和版本。
- user_profile：stage/goal/background（Claim）；constraints：每周可用分钟、预算、风险边界（Claim）。
- evidence_index：{id,source_type,turn,quote,status(active/superseded),verified,url,publisher,access_date,region,role,basis}。
- events：{id,evidence_refs,context,action,independent_part,result,feedback,tool_team_dependency}；后六者为Claim。
- quadrants：固定mind/body/spirit/vocation；各有observation,evidence_refs,potential_strength_ids,limitation,unknown_refs；不得面积/分数伪测量。
- strengths：{id,name,explanation,evidence_refs,event_refs,grade(A/B/C),knowledge_experience_skill,independent_part,repeatability,transferable_skills,application_contexts,boundaries,unknown_refs}。0–3项。
- constraints、opportunities、unknowns、assumptions：约束、机会验证状态、信息缺口和假设索引。unknown记录id/topic/reason/next_check。
- income_basis：currency、unit、tax_basis、period（每年而非累计）、composition；不可混币种与税前税后。
- income_baseline：Claim。income_scenarios固定3项，id A/B/C；每项name、mechanism、status(candidate/exploratory)、strength_ids、evidence_refs、fit_reason、capacity_status、new_capabilities、market_feedback_needed、growth_conditions、inflection_reason、risk、continue_condition、stop_condition、unknown_refs，以及annual。
- annual固定6项，year=0..5，每项value、kind、evidence_refs、assumption_refs、unknown_refs、formula。formula为null或{operation,sum或net；inputs:[Claim]}。数值必须有来源，不需要计算的直接本人输入可formula=null；计算值必须列公式输入。工资按有薪月数与奖金计算，避免重复计提；净贡献先减直接成本；这里sum/net为校验器支持的最小运算，可在文字中保留更完整公式，复杂公式需另核算，不能假称脚本已验证。
- action_plans固定3项，path_id A/B/C；hypotheses、tasks、decision_rules、final_decision(null/continue/adjust/pause)、decision_status(pending/observed)。tasks每路固定7/30/90三阶段，每项name,description,strength_ids,steps,estimated_minutes,estimate_kind,resources,deliverable,metric,completion_rule,feedback_method,risk,fallback,assumption_refs,unknown_refs。未知工时可null，但需unknown_refs；不得声称已可执行验证。
- recommended_path_id与selected_path_id分别为A/B/C/null。reviews含三个审查模块的结果；reports固定REPORT_01/02/03且全部同report_id/revision。

## 报告展示映射
REPORT_01从user_profile/quadrants/strengths/events/constraints提取，额外描述跨维度支持与一个优先问题；无证据的问题称待验证假设。
REPORT_02从income_baseline/scenarios/basis/opportunities提取；比较匹配、条件、投入、不确定性、可逆性，禁止分数；选优不能冒充用户选择。
REPORT_03从selected_path_id与action_plans提取；未选时明确未选，同时保留三路计划。不能在生成当天写“90天后已取得成果”。


## V0.3增补
state分别保存asked_question_count与answered_turn_count，pending_questions最多2项；readiness按runtime记录覆盖及未知原因。analysis应包含cross_dimension_observations与priority_issue；信息不足时明确写待验证假设。最终默认通过模板生成HTML与report.json。


## V0.3.7新增
quadrants每维必须有life_context（生活场景描述或未知）与development（结构见life-and-development.md）。完整访谈state增加life_coverage。各路径可有projection_model与sensitivity；收入analysis_source标ai_model，不把用户desired_income用作annual。assumptions支持有依据的analyst_estimate，无需accepted=true但需rationale与evidence_refs；仍不得编造证据。


V0.3.7新增boundary_analysis，字段与未知处理见boundary-evidence.md。第一部分的折叠薪资参考采用同尺度台阶，三档数值须分别有依据；公式保留内部，页面不展示原始字段。


V0.3.7增加decision_brief、路径reader_cost与value_map、任务feedback_target/review_condition/time_scope及可选reader_summary；字段规则见reader-report.md。renderer将内容审查写入reader_quality，但不修改原始事实；质量未通过的旧数据可以生成初稿，不作已核准建议。




V0.3.7：生成前读取odyssey-and-growth.md，补三路生活蓝图与具体过关信号（未知可显式保留），不可只按工资高低凑三条路。
