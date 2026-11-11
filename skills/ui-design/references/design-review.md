# S6 文档生成与 S7 确认冻结（REVIEW / FROZEN）

## S6 完整性检查（生成前必须跑完）

### 1. 结构完整性

- [ ] 13 个章节齐全，无空章节（每章状态标记不为 pending，或确认为有意空置并说明）
- [ ] 页面结构明确：板块划分可复述
- [ ] 每个组件在第 6 章有定义
- [ ] 第 6/8 章划界清晰：行为只在第 8 章

### 2. 决策完整性

- [ ] pending 列表为空（逐条解决或经用户明确放弃，弃置要记 history）
- [ ] 无 status=confirmed 且 source=ai 的决策（Schema 强制，但仍需人工复核 history 轨迹）
- [ ] 无互相冲突的 confirmed 决策（两条决策对同一事物给出不同值）
- [ ] superseded 链完整：每条 superseded 都指向存在的替代决策，且替代决策已 confirmed

### 3. 数据完整性

- [ ] 每个数据来源明确（静态文件 / 接口）
- [ ] 每个字段有名称、类型、含义、单位，枚举值封闭列出
- [ ] 每个统计数字有口径
- [ ] 页面不使用任何 session 无依据的数据字段

### 4. 交互完整性

- [ ] 每个交互性组件有触发条件、行为、结果三要素
- [ ] 主要异常态有定义：加载失败、数据损坏、列表为空
- [ ] 排序与筛选结论明确（做或不做都是结论）

### 输出格式

```text
Design Validation Report

结构完整性：PASS
决策完整性：PASS
数据完整性：PASS
交互完整性：PASS

未确认事项：0

最终状态：READY_FOR_REVIEW
```

任一维度 FAIL：修复后重跑，不得带病生成。检查通过也只是 READY_FOR_REVIEW，不是冻结。

### 生成 design.md

- 按 templates/design.md 的 13 章结构逐章填写：状态标记、已确认条目引 D-xxx、[MUST]/[SHOULD]/[FORBID] 标注
- 第 13 章决策表与 session decisions 逐 ID 一致（含 superseded 与替代者标注）
- 先更新 session（design_generated、validation_passed、artifact），再写 design.md 文件

## S7 确认与冻结

### 展示内容

向用户汇报：design.md 路径、每章一行摘要、决策总数与关键决策清单、遗留的 SHOULD 建议清单。然后等待用户表态，不催促、不默认冻结。

### 用户可能的操作与处理

| 用户说 | 处理 |
|---|---|
| 「确认」「冻结」「就这样」 | frozen=true、stage=FROZEN、status=completed，history 记 frozen + 时间 + design_version |
| 「第 X 章改成……」 | 走影响分析 → 修改 → 重生成 → 复检 → 再次请求确认 |
| 「把 XX 改回/换方案」 | 走「设计修改与回退」：旧决策 superseded，新决策登记 |
| 「回到 S2 重新讨论结构」 | 解除冻结态（若已冻结先 unfrozen），stage 回退，受影响决策复查并列表告知 |
| 「先停一下」 | session.status=paused，记录进度，等待下次恢复 |

### 修改影响分析（category → 受影响章节）

| 决策 category | 受影响章节 |
|---|---|
| layout, module-set, navigation | 第 4、5、6 章 |
| visual-style, color, typography, density | 第 5、7 章 |
| interaction, chart, list-interaction, list-order, component | 第 6、8 章 |
| data-source, data-scope, data-model | 第 6、9 章 |
| responsive | 第 10 章 |
| tech-constraint | 第 11 章 |
| scope-exclusion | 第 1、6、8、12 章（禁止项出现处） |

分析后向用户报告影响面（含连带验收标准变化），确认后执行；每次修改 design_version 递增；修改后必须重跑完整性检查。

### 冻结后

- design.md 为最终交付物，可交给开发 Agent 实现，或供 ui-implement / ui-review 使用
- 新会话再次打开时：session 已冻结则告知用户「设计已冻结」，询问是查阅还是重新设计（重新设计需用户明确要求解冻）
