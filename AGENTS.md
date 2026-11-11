# AGENTS.md — 仓库开发约定

本仓库是 ui-design-workflow 的 Skill 源仓库。任何 AI Agent（Claude Code、OpenCode、Codex、Pi 等）在本仓库开发时，遵守以下约定。

## 1. 仓库角色

- 本仓库只维护 Skill 源文件、模板、Schema、案例与测试。
- **设计产物不落在本仓库**：design.md 和 `.ui-design/design-session.md` 始终生成在用户正在设计的目标项目根目录。

## 2. 目录职责

| 目录/文件 | 职责 | 变更约束 |
|---|---|---|
| `skills/` | Skill 源文件（唯一源，禁止为某平台复制多份） | 修改 SKILL.md 需检查通用性红线（见第 4 节） |
| `templates/` | 产物标准模板 | 修改需同步评估 examples/ 与 tests/ 是否受影响 |
| `schemas/` | 状态与决策 JSON Schema | 修改字段需同步 templates/ 与 examples/ |
| `examples/` | 真实案例（Benchmark 输入与期望输出） | 案例文件必须能通过 schemas 校验 |
| `tests/` | 自动化检查与 Benchmark | validate-design.py 只依赖标准库优先 |
| `docs/` | 读者向文档 | 过程文档不放这里 |
| `dev-docs/` | 开发过程文档 | 见第 5 节 |
| `dev-examples/` | 开发期沙盒 | 运行产物不提交 |
| `thirdparties/` | 第三方只读参考项目 | 引入必登记 REFERENCES.md |

## 3. Skill 开发规范

- SKILL.md 必须包含 `name` 和 `description` 两个 frontmatter 字段（Agent Skills 基本规范）。
- 详细方法论放 `references/`，按需加载；SKILL.md 本体保持精简，只放触发条件与执行流程。
- 不自创 SKILL.md 格式，遵循开放的 Agent Skills 文件规范。

## 4. 通用性红线

SKILL.md 与 references 中禁止出现：

- 平台独有的提问组件或调用写法（如「调用 AskUserQuestion」）
- 平台独有的 Agent 调度接口
- 平台专属的文件路径变量
- 平台专属的工具调用语法

提问统一表述为：「向用户提出一个当前阶段最重要的问题，等待用户回答后再继续。」

## 5. 开发过程文档

- 需求与架构决策进 `dev-docs/design/`；执行计划进 `dev-docs/planning/`；进度进 `dev-docs/progress/`；阶段报告进 `dev-docs/progress-result/`；踩坑记录进 `dev-docs/experience/`。
- 里程碑完成必须同步更新 `dev-docs/progress/执行进度.md` 与对应阶段的 `dev-docs/progress-result/` 报告。
- 文件命名 kebab-case，日期格式 `YYYY-MM-DD`，编码 UTF-8。

## 6. 验证

- 修改 schemas/ 后，用 `python` + jsonschema 对 templates 与 examples 中的样例数据跑一遍校验。
- `tests/ui-design/validate-design.py`（T4 交付）负责设计文档完整性检查；其运行不依赖第三方库时优先标准库实现。
- 每个 Skill 任务的验收条件见 `dev-docs/planning/2026-11-11-phase1-execution-plan.md`。

## 7. 提交约定

- commit message 中文、动词开头，说明变更范围（如「feat: 新增 ui-design SKILL 七阶段对话规则」）。
- 模板、Schema、示例三者联动变更放在同一个 commit 中，避免中间态破坏校验。
