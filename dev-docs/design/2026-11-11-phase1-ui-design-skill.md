# ui-design-workflow 第一阶段需求：通用 Skill 标准

- 日期：2026-11-11
- 状态：方向与工程决策均已锁定；正式执行计划见 dev-docs/planning/2026-11-11-phase1-execution-plan.md
- 交付目标：通过多轮对话生成经过人工确认的 design.md

## 0. 决策登记

| ID | 决策 | 内容 | 状态 |
|---|---|---|---|
| D-000 | 整体路线 | 采用方案 A：通用 Skill 标准，项目定位为独立的、可跨 Agent 运行的页面设计工作流，不做某个 AI 编程工具的插件集合 | 已确认 |
| D-001 | design.md 默认保存位置 | 当前**目标项目**根目录，直接生成 design.md | 已确认 |
| D-002 | 设计阶段是否生成预览 | 第一版只生成 Markdown 文档 | 已确认 |
| D-003 | GitHub 仓库开源协议 | MIT | 已确认 |

> 关键细节：design.md 保存到用户正在设计的目标项目根目录，而不是本仓库根目录；设计过程状态保存在目标项目的 `.ui-design/design-session.md`。这样设计文档天然属于它所描述的项目，方便后续 ui-implement 直接读取。
>
> ```text
> my-web-project/
> ├── design.md                 最终设计文档
> ├── .ui-design/
> │   └── design-session.md     设计过程状态
> ├── src/
> └── package.json
> ```

## 1. 定位与架构原则

核心设计流程与 Agent 运行环境解耦：Skill 负责方法论，模板负责产物规范，适配层负责不同 Agent 的调用方式。无论 Claude Code、OpenCode、Codex、Pi 还是其他支持 Skill 的 Agent，都不需要重新设计整个流程。

### 三层能力 + 三个 Skill

| 层 | 内容 |
|---|---|
| Skill Layer 工作流层 | ui-design（设计）、ui-implement（实现）、ui-review（验收） |
| Specification Layer 规范层 | design.md（页面设计规范）、design-system.md（视觉设计系统）、design-session.md（设计过程状态）、review-report.md（验收报告） |
| Adapter Layer 运行环境适配层 | Claude Code、OpenCode、Codex、Pi：适配调用入口、文件位置、工具能力和执行约束，不复制核心设计逻辑 |

### 核心架构原则

| 原则 | 具体要求 |
|---|---|
| Agent 无关 | 核心 Skill 使用通用 Markdown 规范 |
| 文件交接 | 不依赖某个 Agent 的内部会话状态 |
| 设计可恢复 | 中断后通过设计状态文件继续 |
| 设计可审计 | 记录每次重要设计决策 |
| 人工可控 | 设计冻结必须经过用户确认 |
| 技术无关 | 不限制最终生成 HTML、React 或 Vue |
| 知识可扩展 | 页面模式、图表模式、视觉风格独立维护 |

> 注意：通用 Skill 不意味着所有 Agent 都能完全一致地运行。各平台的 Skill 加载、工具调用和权限机制可能不同，适配层需要明确平台能力边界。

## 2. 通用 Skill 标准与兼容策略

直接采用开放的 Agent Skills 文件规范，不自创 SKILL.md 格式。标准 Skill 结构：

```text
ui-design/
├── SKILL.md          能力、触发条件、执行流程
├── references/       按需加载的设计方法和规则
├── scripts/          可选辅助脚本
└── assets/           模板、图片等资源
```

标准要求 `name` 和 `description` 两个必要字段，支持渐进式加载，详细知识放 references。

### 2.1 仓库采用唯一源文件

不为每个 Agent 单独维护一套 Skill。`skills/` 下只维护一份 SKILL.md 和 references，通过安装或同步分发：

| 目标环境 | 目录 |
|---|---|
| Claude Code | `.claude/skills/` |
| Codex | `.agents/skills/` |
| OpenCode | `.agents/skills/` |
| Pi 等 | 通过安装脚本或路径配置接入，按各自发现机制适配 |

后续提供安装脚本，只负责同步文件，不修改 Skill 核心内容：

```bash
python scripts/install_skills.py --target codex
python scripts/install_skills.py --target claude
python scripts/install_skills.py --target opencode
```

### 2.2 通用性约束

SKILL.md 中禁止依赖：

- 某个平台独有的提问组件
- 某个平台独有的 Agent 调度接口
- 某个平台专属的文件路径变量
- 某个平台专属的工具调用语法

不写「调用 AskUserQuestion」，而是写「向用户提出一个当前阶段最重要的问题，等待用户回答后再继续」。平台具备专用提问能力时可在适配层使用，不影响通用流程。

## 3. 第一阶段文件设计

第一阶段只把 ui-design 做完整，不提前实现另外两个 Skill。

```text
ui-design-workflow/
├── skills/ui-design/
│   ├── SKILL.md                    核心
│   ├── references/
│   │   ├── discovery.md
│   │   ├── information-architecture.md
│   │   ├── visual-design.md
│   │   ├── interaction-design.md
│   │   └── design-review.md
│   ├── templates/
│   │   ├── design.md
│   │   ├── design-session.md
│   │   └── design-system.md
│   ├── schemas/
│   │   └── design.schema.json
│   └── examples/dashboard/
│       ├── input.md
│       ├── design.md
│       └── design-session.md
├── tests/ui-design/
│   ├── cases/
│   ├── expected/
│   └── validate-design.py
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md
└── docs/compatibility.md
```

三个核心产物文件的区分（不能混成一个文件）：

- `design.md`：单个页面或项目的设计交付文档
- `design-system.md`：可跨页面复用的视觉规范
- `design-session.md`：当前设计任务的进度与决策记录

## 4. ui-design 执行逻辑

第一版采用严格的对话式设计，但不要求每个项目都走完所有问题。

### 4.1 七个阶段

| 阶段 | 核心任务 | 输出 |
|---|---|---|
| S1 需求理解 | 用户、目标、场景、资料 | 需求摘要 |
| S2 信息架构 | 页面区域、导航、内容层级 | 页面结构 |
| S3 视觉设计 | 风格、色彩、字体、密度 | 视觉规范 |
| S4 交互设计 | 图表、组件、操作反馈 | 交互规范 |
| S5 数据与技术 | 数据来源、字段、技术约束 | 数据规范 |
| S6 文档整理 | 汇总并检查设计完整性 | design.md |
| S7 人工确认 | 修改、复核、冻结 | 最终设计文档 |

阶段推进规则：

- 不是每个阶段都必须逐项提问。用户已明确要求（如单页面纵向布局、现代简洁浅色风格、舒适型信息密度）直接记录为已确认决策，不再重复提问
- 用户在后期阶段（如 S5）修改早期结论（如 S2 页面结构）时，需检查受影响的视觉和交互设计，而不是简单覆盖之前的所有决策

### 4.2 设计状态文件

```yaml
schema_version: 1

project:
  name: prd-quality-dashboard
  output: design.md

session:
  stage: interaction
  status: in_progress
  frozen: false

decisions:
  - id: D-001
    category: layout
    value: single-page
    status: confirmed

  - id: D-002
    category: visual-style
    value: light-saas
    status: confirmed

  - id: D-003
    category: density
    value: comfortable
    status: confirmed

pending:
  - id: Q-001
    category: interaction
    description: 是否需要问题详情抽屉

history: []
```

决策状态统一取值（保留设计演变过程）：

| 状态 | 含义 |
|---|---|
| confirmed | 用户已经确认 |
| proposed | AI 提出的建议 |
| pending | 等待用户回答 |
| superseded | 被后续决定替代 |

## 5. 第一阶段执行计划（初版 T1～T5，已被正式计划取代）

> 正式执行计划升级为 6 个任务（T4 设计完整性检查独立成项，T6 跨 Agent 兼容性验证），见 [dev-docs/planning/2026-11-11-phase1-execution-plan.md](../planning/2026-11-11-phase1-execution-plan.md)。本节保留作为演进记录。

| 任务 | 优先级 | 内容 | 验收 |
|---|---|---|---|
| T1 仓库基础架构 | P0 | 建立目录结构；编写 ARCHITECTURE.md、README.md；明确通用 Skill 规范；确定文件交接协议 | 仓库结构、规范和职责边界明确 |
| T2 设计文档标准 | P0 | 编写 design.md / design-session.md 模板；定义设计决策格式；定义冻结与回退机制；编写 JSON Schema | 设计文档可人工阅读，也可被后续 Skill 稳定解析 |
| T3 ui-design Skill | P0 | 编写 SKILL.md；实现七阶段对话规则；单问题提问机制；决策记录和上下文恢复；设计完整性检查 | 从模糊需求出发，多轮问答生成完整设计文档 |
| T4 Dashboard 实战案例 | P1 | 用之前的 PRD Dashboard 作输入重跑 ui-design，生成 design.md；与原人工方案对比；记录遗漏和重复提问 | 关键决策完整保留 |
| T5 Skill 兼容与评测 | P1 | 检查 SKILL.md 格式；测试 Codex / Claude Code / OpenCode；测试中断恢复与设计回退；建立固定 Benchmark | 核心设计流程不依赖特定 Agent 专有工具 |

## 6. 第一阶段 DoD（硬性验收条件）

| 验收项目 | 通过条件 |
|---|---|
| 通用格式 | 符合 Agent Skills 基本规范 |
| 对话设计 | 支持多轮问答 |
| 问题控制 | 不重复询问已确认信息 |
| 设计阶段 | 七阶段流程能够正常推进 |
| 状态恢复 | 中断后能够恢复设计 |
| 设计修改 | 支持修改之前的决定 |
| 设计冻结 | 未确认不能标记为冻结 |
| 文档生成 | 完整生成 design.md |
| 文档检查 | 必填章节、未确认项检查通过 |
| 案例测试 | Dashboard 案例完整通过 |

使用开放规范的验证工具检查 Skill 文件结构，并针对各 Agent 分别测试实际加载效果。

## 7. 第一阶段明确不做什么

- 不开发 HTML 页面生成器
- 不开发 React/Vue 代码生成器
- 不开发 Figma 插件
- 不开发设计画布
- 不开发截图视觉对比
- 不开发自动修复页面
- 不开发多 Agent 并行设计

第一阶段只验证一个核心问题：AI 能否通过有组织的多轮问答，把模糊的页面需求变成一份准确、完整、可交付给开发 Agent 的 design.md？

## 8. 三个工程细节（已锁定）

1. design.md 默认保存位置：A. 目标项目根目录（已确认）
2. 设计阶段是否生成预览：A. 第一版只生成 Markdown（已确认）
3. GitHub 仓库开源协议：MIT（已确认）

## 引用

- Open Agent Skills 规范：https://openagentskills.dev
- OpenCode Skills 文档：https://docs.opencode.ai（支持 `.agents/skills/`、`.claude/skills/` 等兼容目录）
