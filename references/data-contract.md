# V0.4.0 数据契约：V1.1 五屏互动报告

以 `examples/虚构演示-未知收入.json` 为完整字段模板，按实际访谈重写内容后保存为 UTF-8 JSON。示例是虚构人物，任何文字和数据都不能当新用户事实。所有顶层与示例中的字段必须存在；无数据用 `null`，集合用 `[]`；不要写“0”来代表未知。可用标准库：`python scripts/render_report.py /路径/访谈数据.json /路径/个人报告.html`。运行时从本包 assets 读取模板，生成单文件 HTML；使用方无需联网打开。

## 数据字段与内容深度
- `schema_version` 固定 `0.4.0`；`meta.demo` 真实报告为 false；`income_unit` 为统一单位（如“万元/年”）；`income_basis` 说清税前/税后、工资与其他收入、成本及来源边界。`selected_path` 只有用户明确选择才填 A/B/C；`recommended_path` 可以记录 AI 建议，两者都可 null。
- `evidence` 每条 `id` 唯一，`kind` 是 `user`（本人原话/访谈事实）或 `market`（外部来源）；`quote` 保存简短原话或来源摘要，外部 `url` 为 http(s) 且 `access_date` 是实际访问日期。无来源链接为 null。引用使用 `evidence_refs` 数组。不能将自己的推断、假设标为用户原话，不能把未核验资料标为市场证据。
- `vision.words` 最多6项：`title`、`meaning`（区分本人表达/归纳）、`quote`（本人原话或 null）、`evidence_refs`；`priority` 是本人确认的零基索引或 null；`boundaries` 是本人明确边界的字符串数组，不得由 AI 代选。可展开区域显示说明及依据；用户改优先级为临时状态。
- `starting` 的 `title`、`observation`、`caveat` 说明已知/未知；`nodes` **恰好三项**，通常分配预算、时间责任、资金缓冲；每项 `label`、`title`、`summary`、`detail`、`evidence_refs`；`stats` 数组每项 `label`、`value`（可 null）。长分析进 detail。无基础不要算自由日期。
- `dimensions` 必须包含 mind、body、spirit、vocation。各项 `observation`、`action`、`signal`、`limit`、`detail`、`evidence_refs`，内容为观察、下一步、反馈、局限及深度说明；未证实标待验证。`level` 可为 1、2、3 或 null；`phase` 可为 `dissonance`、`uncertainty`、`discovery` 或 null；不够证据时填 null。Human 3.0 是启发框架，不是测评和诊断。
- `strengths` 0–3 项：`name`、`summary`、`action`、`signal`、`limitation`、`detail`、`evidence_refs`；`fragments` 最多4项，每项 `label`、`text`、`evidence_refs`。在 detail 区分具体行为、可迁移之处、反差、支持与反例和机会验证；素材不足则不强凑。读者可以切换各项并查看证据。
- `paths` 按 A、B、C 排序恰好3项；每项 `id`、`name`、`where`、`value`、`income`、`requirements`、`risk`、`lifestyle`、`detail`、`evidence_refs`、`assumptions`。无依据的路径可命名为“探索槽”，正文写明待确认。detail 填具体生活画面、收入机制、为什么入选与被排除选项、目标用户与机会、进入门槛、对照和反证；不能把关注度当成收入保证。
- 每路 `annual` 是 Y0–Y5 六项，包含 `year`（整数0–5）、`value`（数字或 null）、`basis`（计算口径与公式或 null）、`evidence_refs`。三路 Y0 相同；未来数值须有 assumptions、公式及可追溯市场来源，用户事实也应有引用；资料不足就 null。校验程序只检查字段和引用，**不能判断来源可靠性、适用性或公式正确性**；需人工核实。某年未知时，图仅呈现无金额比例的分岔路径，不插值、不以横向位置暗示收入差距。
- 每路 `plan` 依次是 `day` 30、90、365，`title`、`action`、`output`、`feedback`、`time`、`detail`、`evidence_refs`。detail 展开对象、操作步骤、总工时/周期、成本、可观察反馈、继续/调整/停止条件与失败回退；不知时写待确认。计划各自独立，切换路径不视为执行。自动选择 A 是“查看”，不表示用户已选。

## 校验与安全
渲染器验证基本类型、长度、引用完整性、Y0一致及未来数值须关联带 URL/访问日期的市场证据；它不联网、不会替你研究或验证内容。文本嵌入和展示时转义 HTML/脚本；不要向数据输入凭据、秘密或不必要的敏感信息。输出 JSON 与 HTML 均包含访谈内容，请自行保管。可结合 `tests/test_browser.py` 用本机 Playwright 复测，但脚本运行与打开报告本身只需要 Python 标准库和浏览器。
