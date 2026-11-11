---
name: ui-design
description: 通过多轮对话理解页面需求，完成信息架构、布局、视觉、交互和数据设计，最终生成经过用户确认的 design.md。当用户想设计一个新页面、优化已有页面结构、根据业务需求生成页面设计文档，或提供参考网站/图片希望分析并转化为页面设计时使用。适用于先设计再开发的工作方式。
---

# ui-design — 页面设计工作流

通过七阶段多轮问答，把模糊的页面需求变成一份准确、完整、可交付给开发 Agent 的 design.md。
设计优先，代码后置：本 Skill 只产出设计文档，不生成页面代码。

## 核心规则（任何阶段不可违反）

1. **平台无关**：向用户提问时使用普通对话（「向用户提出一个当前阶段最重要的问题，等待用户回答后再继续」），不假设存在任何特定 Agent 的提问组件或工具接口
2. **单问题优先**：每轮只提出一个核心问题，可附 2～4 个选项；用户一次回答多个问题时照单全收
3. **不重复提问**：用户已明确表达的要求，直接登记为 confirmed 决策（记录 source=user），后续阶段不得再问
4. **给出推荐**：每次提问附上推荐方案与理由，用户可以只回复「同意推荐」
5. **修改做影响分析**：用户修改早期决策时，先分析受影响的章节与决策，向用户说明影响面，再执行修改
6. **未经确认不冻结**：frozen 只能由用户在 S7 明确确认后设置
7. **不擅自补齐业务规则**：关键业务规则（统计口径、字段含义、操作边界）缺失时列为 pending 问题，不得自行编造
8. **先 session 后 design**：任何状态变化先写入 design-session.md，再落到 design.md

## 启动：新建或恢复会话

在目标项目根目录（用户当前工作的项目，不是本 Skill 所在目录）检查 `.ui-design/design-session.md`：

- **存在** → 读取该文件恢复会话：跳过所有 confirmed 决策对应的话题，从中断的 stage 继续，并向用户说明「已恢复，当前处于 X 阶段，剩余待确认：pending 列表」；history 追加一条 `session_resumed`
- **不存在** → 从本 Skill 的 templates/ 复制 `design-session.md` 到目标项目 `.ui-design/design-session.md`，填写 project.name（取目标项目名），开始 S1

templates/ 目录指本 Skill 包内的 templates（design.md、design-session.md）。目标项目如已有 design.md，按「文件写入规则」第 1～3 条处理。

## 七阶段流程

按顺序推进，允许按用户要求回退到任一早期阶段。每阶段开始前读取对应 reference：

| 阶段 | 读取 | 目标 | 输出 | 完成条件 |
|---|---|---|---|---|
| S1 DISCOVERY | references/discovery.md | 用户、目标、场景、资料、限制 | 需求摘要（用户确认） | 用户确认摘要，输入中已明确项已登记 |
| S2 STRUCTURE | references/information-architecture.md | 页面数量、区域、层级、导航 | 页面结构方案（用户确认） | 板块划分与层级确认 |
| S3 VISUAL | references/visual-design.md | 风格、色彩、字体、密度 | 视觉规范（用户确认） | 风格/主色/密度确认 |
| S4 INTERACTION | references/interaction-design.md | 组件行为、图表、反馈 | 交互规范（用户确认） | 每个组件的行为有归属 |
| S5 DATA | references/information-architecture.md（数据节）+ discovery.md 数据三问 | 数据来源、字段、口径、技术约束 | 数据与技术规范（用户确认） | 无 pending 的数据类问题 |
| S6 REVIEW | references/design-review.md | 完整性检查、生成 design.md | design.md 初版 | 检查通过（READY_FOR_REVIEW） |
| S7 确认冻结 | references/design-review.md | 修改、复核、冻结 | 冻结的 design.md | 用户明确确认后 frozen=true |

阶段推进规则：

- 用户在早期阶段已明确表达的要求，在对应阶段直接作为已确认方案呈现，只做复述确认（「你在需求里说过 X，我按此执行」），不重新提问
- 每个阶段结束时做阶段性总结：已确认决策列表 + 本阶段新增 pending
- 用户在后期阶段提出早期阶段的修改（如在 S5 改 S2 的结构）：回到该决策的影响分析流程（见「设计修改与回退」），不简单覆盖

## 多轮问答规则

- 每轮消息结构：当前阶段上下文一句话 → 核心问题 → 选项（2～4 个，含推荐标记与理由）→ 提示用户可自由回答
- 用户跳过问题（回答「你定」）：按推荐方案登记为 confirmed，但 source 标 user、history 的 detail 注明「用户委托 AI 决定」
- 用户一次给出多项信息：逐项拆解登记，缺失项只针对缺失部分继续提问
- 参考网站/图片：归纳其结构、风格、交互模式为 proposed 决策，经用户确认后转 confirmed

## 决策与问题管理

- 决策 ID：`D-` 三位数字，按创建顺序递增，不复用；问题 ID：`Q-` 三位数字，同规则
- 决策状态：`proposed`（AI 提议）→ `confirmed`（用户确认，此时 source 必须为 user）→ 可变 `superseded`（必须写 superseded_by）；`pending`（等待用户回答）
- pending 解决后移入 history（question_resolved），pending 列表不保留已解决项
- 复合值（如板块清单、图表组合）用 YAML 列表，不用自由文本拼接
- 常用 category 词表：`audience, layout, navigation, module-set, content, visual-style, color, typography, density, component, interaction, chart, list-interaction, list-order, data-source, data-scope, data-model, responsive, tech-constraint, scope-exclusion, acceptance, other`
- 任何决策、问题、阶段变化都同步追加 history（只追加，不修改）

## 设计修改与回退

用户要求修改某个已确认决策（「TOP5 改成 TOP3」「背景换成深色」）时：

1. 定位该决策及其 superseded 链
2. 影响分析：按 category 找受影响章节——layout/module-set → 第 4、5、6 章；visual-style/color/typography/density → 第 5、7 章；interaction/chart/list-* → 第 6、8 章；data-source/data-scope/data-model → 第 6、9 章；responsive → 第 10 章；tech-constraint → 第 11 章
3. 向用户说明影响面与连带决策（如「清单分页取消后，第 12 章验收标准第 6 条也要改」），确认后执行
4. 新决策登记（旧决策标 superseded），先更新 session，再更新 design.md 受影响章节，design_version 递增
5. 回退到早期阶段时，该阶段之后受影响的 proposed/pending 决策一并复查，向用户列出受影响清单

## 生成设计文档（S6）

1. 运行完整性检查（清单见 references/design-review.md）：结构完整性、决策完整性、数据完整性、交互完整性
2. 存在未解决的 pending：逐条向用户确认（解决或明确放弃），不得带未决问题生成
3. 检查通过后，按 templates/design.md 的 13 章结构生成 design.md：每章状态标记、已确认条目引用 D-xxx、待确认引用 Q-xxx、[MUST]/[SHOULD]/[FORBID] 分级标注
4. 第 13 章决策表必须与 session decisions 逐 ID 一致（含 superseded 标注）
5. 输出检查结果摘要：四个维度 PASS/FAIL + 未确认事项数 + 最终状态（READY_FOR_REVIEW / FAILED）
6. 先更新 session（design_generated、validation_passed/failed、artifact 字段），再写入 design.md

## 确认与冻结（S7）

1. 向用户展示：design.md 位置、设计摘要（每章一行）、决策总数与关键决策、剩余 SHOULD 建议
2. 用户可以：确认冻结、修改某章节（走「设计修改与回退」）、重新讨论某决策、回退到早期阶段、暂停（session.status=paused）
3. **只有用户明确表达确认（如「确认」「冻结」「就这样」）才可设置 frozen=true、stage=FROZEN、status=completed**，并在 history 记录 frozen 与冻结时间、design_version
4. 用户要求重新设计：解冻（unfrozen），回退到指定阶段继续
5. 冻结后 design.md 即交付物，可直接交给开发 Agent 实现或后续 ui-implement / ui-review Skill 使用

## 文件写入规则

1. 首次生成 design.md 前检查目标文件是否存在
2. 已存在则不允许静默覆盖：向用户展示现有文件要点，经确认后才能覆盖或另存新版本
3. 设计过程中 design.md 未生成时，所有状态只进 session
4. 修改设计时先更新 session，再更新 design.md
5. 冻结时记录冻结时间和设计版本（design_version 递增）
6. 用户要求重新设计时允许解除冻结

## references 索引（按需加载，进入阶段前读取）

| 文件 | 内容 |
|---|---|
| references/discovery.md | S1 需求理解：问题清单、需求摘要模板、直登规则、数据范围三问 |
| references/information-architecture.md | S2 信息架构：页面骨架模式、区域划分、内容层级 + S5 数据规范 |
| references/visual-design.md | S3 视觉设计：风格词表、色彩体系、字体层级、密度三档 |
| references/interaction-design.md | S4 交互设计：图表选型映射、组件行为清单、反馈方式 |
| references/design-review.md | S6/S7：完整性检查清单、检查输出格式、冻结流程、影响分析 |

## 产物位置

- `design.md` → 目标项目根目录（设计的归属项目）
- `.ui-design/design-session.md` → 目标项目根目录下（设计过程状态，唯一恢复点）
- 本 Skill 不在其他任何位置写文件
