# 三种未来与具体增长门槛

本产品是“个人优势变现地图”。奥德赛计划用于拓展不同未来，薪酬研究用于查收入边界，四维访谈用于了解本人；任何框架都不能直接推出年薪。借鉴Designing Your Life三种五年人生构想，不冒称官方测评，不复制题库。方法来源：https://designingyour.life/insights/the-magic-of-odysseys-prototyping-your-future-with-designing-your-life/

## 访谈与方案差异
除现有四维覆盖，询问当前道路若不能继续会选择什么，以及若评价和收入压力暂时减轻最想探索什么；根据已提供答案选一个缺口，每轮最多两个独立短问，不机械追加全部问题。探索愿望不是可行性结论。三路必须在工作内容/收入机制、日常时间与地点、生活价值与关系安排、风险与资源中至少有两项实质差异；差异不足明确“职业走法候选，第三种人生方向待补”，不硬凑辞职、创业或副业。

## 新增数据
income_scenarios[].life_blueprint={daily_life,work_style,time_and_relationships,tradeoff,curiosity,milestones,status_note,evidence_refs,assumption_refs,unknown_refs}。milestones是第1/3/5年各自的生活与职责条件里程碑，不复制年度金额或7/30/90天任务。每项都是claim对象（kind,value,evidence_refs,assumption_refs,unknown_refs）；没有信息用unknown claim，推演生活安排用assumption/inference，不能写成本人愿望。status_note用简短字符串说明这是候选方案还是经本人表达的未来设想；不将自评喜欢自动视为可行。
income_scenarios[].growth_checkpoint={obstacle,pass_signal,pause_signal,evidence_refs,assumption_refs,unknown_refs}；前三项也使用claim。obstacle须对应当前路径的真实缺口；pass_signal必须有具体对象、产物、可观察结果及检验窗口，阈值由AI提出时标假设；pause_signal对应预算、容量、风险或窗口失效。阈值不是成功概率；缺反馈不能直接证明无需求。

## 不重复的阅读分工
01先展示三路曲线；一句优先建议；随所选路径显示生活样貌、适配依据、收入机制、代价及一项过关证据。当前收入与薪资样本只在折叠参考里解释；薪资上沿不是个人天花板。原始参数仅留数据文件。未来收入依个人贡献、实际市场锚点、回报机制和资源约束测算；生活蓝图更新若改变投入、转换期或付费对象，重算收入并重审计划。
02四维图回答“你目前怎么发挥、优势有什么依据”；内侧细弧显示阶段，外侧显示层级及该层阶段。发现细弧亮满，未知层级不填外圈；这不是科学评分。优势最多三项，不再重讲每路收入。
03按A/B/C切换优势→对象→交付→收入机制→验证，展示已优化的7/30/90天具体流程。顶部切换与收入图/行动保持联动；“全部点亮”只是曲线比较，不篡改本人选择。

## 审查
三种人生蓝图若只改职位名称或年度金额不合格；所有建议不可只写“提升能力、积累资源、抓住机会”。必须给出对象、证据、门槛与回退条件；缺少资料只标一处关键缺口。审查三路生活约束、收入模型与行动投入是否同源，避免用同一份空闲时间叠算三条并行收入。
