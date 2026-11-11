# ui-design-workflow

一套独立的、可跨 Agent 运行的 UI 页面设计工作流。核心设计流程与 Agent 运行环境解耦：Skill 负责方法论，模板负责产物规范，适配层负责不同 Agent 的调用方式。

在 Claude Code、OpenCode、Codex、Pi 或任何支持 Agent Skills 的环境中，都能运行同一套设计流程。

## 工作流组成

| Skill | 职责 | 状态 |
|---|---|---|
| ui-design | 多轮对话完成页面设计，产出经人工确认的 design.md | Phase 1 开发中 |
| ui-implement | 按 design.md 完成前端实现 | 规划中 |
| ui-review | 按 design.md 验收标准验收 | 规划中 |

## ui-design 是什么

用户描述一个模糊的页面需求，ui-design 通过七阶段多轮问答（需求理解 → 信息架构 → 视觉设计 → 交互设计 → 数据与技术 → 文档生成 → 人工确认），逐步把需求变成一份准确、完整的设计文档：

- 产物落在**你的目标项目**根目录：`design.md`（设计交付物）+ `.ui-design/design-session.md`（设计过程状态，可中断恢复）
- 已确认的决策不重复询问；用户可随时修改之前的决定
- 未经用户确认不会冻结设计
- 不绑定具体前端技术，不生成页面代码

## 安装（Phase 1 手动方式）

把 `skills/ui-design/` 复制到对应 Agent 的 Skill 目录：

| Agent | 目标目录 |
|---|---|
| Claude Code | `<项目>/.claude/skills/ui-design/` |
| Codex / OpenCode | `<项目>/.agents/skills/ui-design/` |
| Pi 等其他环境 | 按各自 Skill 发现机制配置路径 |

安装脚本与兼容性说明在后续版本提供（见 docs/compatibility.md，T6 产出）。

## 使用

在支持 Agent Skills 的工具中对 Agent 说：

```text
帮我设计一个页面：一个面向管理层的数据看板，单页面，现代简洁浅色风格
```

Agent 将进入 ui-design 流程：分阶段提问、记录决策、生成并确认设计，最终在你的项目根目录生成 `design.md`。中断后重新进入，凭 `.ui-design/design-session.md` 继续设计。

## 目录结构

```text
skills/ui-design/   Skill 源文件（唯一源，安装时复制到各 Agent 目录）
templates/          产物标准模板（design.md、design-session.md、design-system.md）
schemas/            状态与决策 JSON Schema
examples/           实际设计案例（Benchmark）
tests/              自动化检查与 Benchmark
docs/               读者向文档
dev-docs/           开发过程文档（需求、计划、进度、经验）
```

## 开发状态

当前处于 Phase 1（只做 ui-design，只生成 Markdown）。执行计划与验收标准见 [dev-docs/planning/2026-11-11-phase1-execution-plan.md](dev-docs/planning/2026-11-11-phase1-execution-plan.md)，架构见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## License

[MIT](LICENSE)
