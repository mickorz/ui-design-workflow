---
schema_version: 1
design_version: 0.2.0
status: frozen
frozen: true
generated_at: "2026-11-11 10:20"
session: .ui-design/design-session.md
---

# PRD 质量数据看板 设计文档

> 本文档由 ui-design 工作流生成，是设计交付物，交给开发 Agent 实现时不允许产生歧义。
> 设计过程与决策轨迹见 `.ui-design/design-session.md`。
>
> 标记约定：
>
> - `[MUST]` 必须实现的要求，开发时不可省略
> - `[SHOULD]` 设计建议，实现时可与用户协商调整
> - `[FORBID]` 禁止擅自修改的约束，违反即偏离设计
>
> 章节状态约定：`confirmed`（该章内容全部经用户确认）/ `partial`（部分确认）/ `pending`（尚无已确认内容）。

## 1. 项目背景

> 章节状态：confirmed

**已确认**

- 本页面用于产品部 PRD（产品需求文档）质量的月度汇报，属于部门质量汇报流程的展示层（D-001）
- 页面只读，仅用于查看与分析结果展示（D-002）

**待确认**

**约束**

- [MUST] 页面定位为汇报型看板，服务于月度质量汇报会议
- [FORBID] 不得加入任何裁决、处理、流转类功能或操作入口（D-002）

## 2. 页面目标

> 章节状态：confirmed

**已确认**

- 让高层在 3 分钟内掌握当月 PRD 质量全貌：趋势是否恶化、哪些模块风险高、典型问题是什么（D-001）
- 领导问到任意一个问题时，能在完整清单中直接查到（D-004）

**待确认**

**约束**

- [MUST] 核心结论（趋势向好或恶化、高风险模块）必须在首屏可感知
- [SHOULD] 页面适合会议室投屏展示

## 3. 用户与使用场景

> 章节状态：confirmed

**已确认**

- 目标用户：公司高层，非产品角色，无 PRD 专业背景假设（D-001）
- 使用场景：月度质量汇报会议投屏讲解；会后通过链接自行查阅（D-001）
- 使用时长：单次 3 至 10 分钟

**待确认**

**约束**

- [MUST] 信息表达使用业务语言，避免测试、研发内部术语
- [MUST] 桌面端优先，目标分辨率 1920×1080

## 4. 信息架构

> 章节状态：confirmed

**已确认**

- 单页面纵向滚动布局，无路由、无页面跳转（D-003）
- 四个板块自上而下：概览图表区 → 风险分析区 → TOP 5 问题区 → 完整问题清单区（D-004）
- 内容层级三级：页面标题 → 板块标题 → 板块内卡片/表格

**待确认**

**约束**

- [MUST] 板块顺序固定为 D-004 所列顺序，风险分析在 TOP 5 与清单之前
- [SHOULD] 页头提供板块锚点导航

## 5. 页面布局

> 章节状态：confirmed

**已确认**

- 页头：页面标题 + 数据周期（本月）标识，单行
- 概览图表区：三张图表卡片横向排列（趋势折线、问题分布环图、模块对比柱状图，见 D-008）
- 风险分析区：全宽风险矩阵卡片
- TOP 5 问题区：全宽列表卡片
- 完整问题清单区：全宽数据表格
- 内容区最大宽度 1200px，水平居中

**待确认**

**约束**

- [MUST] 板块之间以留白分隔，不使用分隔线堆叠
- [MUST] 舒适型密度：卡片内边距不小于 16px，卡片间距不小于 16px（D-007）

## 6. 内容与组件定义

> 章节状态：confirmed

**已确认**

- 页头组件：标题文字 + 数据周期徽标
- 概览图表区组件：
  - KPI 指标行：问题总数、本月新增、本月关闭、遗留未关闭，四个指标卡
  - 质量趋势折线图：近 6 个月问题数走势
  - 问题分布环图：按严重度分布
  - 模块对比柱状图：各模块问题数对比
- 风险分析区组件：风险矩阵（横轴模块，纵轴严重度，格子颜色表示风险等级）
- TOP 5 问题区组件：编号列表，每项含标题、所属模块、严重度徽标、一句话摘要
- 完整问题清单区组件：数据表格，列固定为：ID、标题、所属模块、严重度、状态、提出日期

**待确认**

**约束**

- [MUST] 所有板块只展示数据，不提供任何操作控件（D-002）
- [FORBID] 清单区不得出现分页控件；数据量以本月快照为准一次展示（D-014）

## 7. 视觉设计规范

> 章节状态：pending

**已确认**；页面底色浅灰白，卡片白色
- 主色：稳重蓝 #2563EB（D-006），用于标题强调、图表主系列、链接
- 语义色按严重度四级：致命（红 #DC2626）、严重（橙 #EA580C）、一般（黄 #CA8A04）、轻微（灰 #6B7280）
- 字体：系统字体栈（system-ui）；页面标题 24px、板块标题 18px、正文 14px、辅助文字 12px
- 卡片：圆角 8px，浅阴影，白底
- 信息密度：舒适型（D-007）

**待确认**

**约束**

- [MUST] 严重度配色全页面统一，不得每板块自定义颜色
- [SHOULD] 图表配色以主色为基准派生，保持整体协调

## 8. 交互设计

> 章节状态：confirmed

**已确认**

- 图表交互：鼠标悬浮显示数值提示（tooltip），不提供图例点选等复杂交互（D-008）
- 清单详情：悬浮提示展示问题描述等详情字段（D-011）
- 清单排序：按严重度降序固定排列，不提供排序切换（D-010）
- 板块锚点：页头锚点点击后平滑滚动至对应板块

**待确认**

**约束**

- [FORBID] 不得实现行内展开动画（D-009 已被 D-011 替代）
- [FORBID] 不做时间范围筛选、模块筛选等任何筛选交互（D-014）
- [MUST] 所有悬浮提示在鼠标移开后消失，不遮挡相邻内容

## 9. 数据结构与数据来源

> 章节状态：confirmed

**已确认**

- 数据来源：静态 JSON 文件，与页面同目录，页面加载时读取（D-012）
- 数据范围：仅本月快照，无历史切换（D-014）
- 字段定义：
  - `summary`：`{ total, new_this_month, closed_this_month, remaining }`，四个整数
  - `trend`：`[{ month, issue_count }]`，近 6 个月
  - `issues[]`：`{ id, title, module, severity, status, created_at, summary }`；severity 取值 fatal / serious / minor / trivial；status 取值 open / closed
  - `modules[]`：`{ name, issue_count, risk_level }`；risk_level 取值 high / medium / low
- 统计口径：遗留未关闭 = 已提出且状态为 open 的问题数；趋势按自然月聚合

**待确认**

**约束**

- [FORBID] 页面不得使用本文档与 session 未定义的数据字段
- [MUST] JSON 解析失败时页面显示明确的错误提示，不显示空白看板

## 11. 技术约束

> 章节状态：confirmed

**已确认**

- 最终交付：单文件静态 HTML（D-013），CSS 与 JS 内嵌，静态 JSON 数据文件随附（D-012）
- 图表渲染：使用 ECharts（CDN 引入）
- 浏览器目标：Chrome、Edge 最新稳定版

**待确认**

**约束**

- [MUST] 无构建工具、无后端依赖，双击 HTML 即可打开
- [SHOULD] JSON 加载失败或 CDN 不可用时给出可见错误提示

## 12. 页面验收标准

> 章节状态：confirmed

**已确认**

- 1920×1080 分辨率下无横向滚动条
- 四个板块齐全且顺序为：概览图表区、风险分析区、TOP 5 问题区、完整问题清单区
- 三张图表正常渲染，无 console 报错
- KPI 四项指标与 JSON 的 summary 字段一致
- 完整清单包含第 6 章定义的全部六列，按严重度降序排列（D-010）
- 清单悬浮可见详情提示，无行内展开交互（D-011）
- 页面无任何操作按钮、筛选控件或裁决入口（D-002、D-014）
- 全页面使用第 7 章定义的语义色与主色，浅色主题（D-005、D-006）
- 数据 JSON 缺失或损坏时显示明确错误提示

**待确认**

**约束**

- 本章节条目即 ui-review 的验收清单，逐条可检查

## 13. 设计决策记录

> 章节状态：confirmed

> 本章节是全部设计决策的汇总视图，与 `.ui-design/design-session.md` 的 decisions 一致。
> 被 superseded 的决策保留在表中并注明替代者，形成可追溯的演变记录。

| ID | 类别 | 决策描述 | 值 | 状态 | 来源 | 替代者 |
|---|---|---|---|---|---|---|
| D-001 | audience | 受众为公司高层，页面定位为汇报型看板 | executive | confirmed | user | - |
| D-002 | scope-exclusion | 不包含任何裁决或处理问题的功能，页面只读 | no-adjudication | confirmed | user | - |
| D-003 | layout | 页面采用单页面纵向滚动布局 | single-page-vertical | confirmed | user | - |
| D-004 | module-set | 四个板块：概览图表、风险分析、TOP 5 问题、完整清单 | overview-charts, risk-analysis, top5-issues, full-list | confirmed | user | - |
| D-005 | visual-style | 现代简洁浅色风格 | light-modern-saas | confirmed | user | - |
| D-006 | color | 主色稳重蓝，语义色按严重度四级 | steady-blue | confirmed | user | - |
| D-007 | density | 信息密度舒适型 | comfortable | confirmed | user | - |
| D-008 | chart-set | 图表组合：趋势折线、分布环图、模块柱状 | trend-line, issue-donut, module-bar | confirmed | user | - |
| D-009 | list-interaction | 问题清单行内展开详情 | row-expand | superseded | user | D-011 |
| D-010 | list-order | 清单按严重度降序 | severity-first | confirmed | user | - |
| D-011 | list-interaction | 详情用悬浮提示，无展开动画 | hover-tooltip | confirmed | user | - |
| D-012 | data-source | 静态 JSON 数据，不接后端 | static-json | confirmed | user | - |
| D-013 | tech-constraint | 单文件静态 HTML 交付 | static-html | confirmed | user | - |

> 冻结记录：2026-11-11 10:20，design_version 0.2.0，经用户明确确认冻结。
