---
# ui-design 设计过程状态文件（唯一恢复点）
# 保存位置：目标项目根目录下 .ui-design/design-session.md
# 新会话凭本文件继续设计，不依赖任何 Agent 的内部会话状态。
# 本文件与 templates/design-session.schema.json、schemas/design-decision.schema.json 对应。

schema_version: 1

# 目标项目信息（design.md 的归属项目，不是 ui-design-workflow 仓库）
project:
  name: ""                # 项目名（必填）
  output: design.md       # 设计文档文件名
  output_dir: "."         # 输出目录，默认目标项目根目录

# 会话状态
session:
  # 当前阶段，只允许：DISCOVERY | STRUCTURE | VISUAL | INTERACTION | DATA | REVIEW | FROZEN
  stage: DISCOVERY
  # 任务状态：in_progress（进行中）| paused（用户暂停）| completed（本任务结束）
  status: in_progress
  # 是否冻结。frozen 为 true 当且仅当用户在 S7 明确确认，且 stage 必须为 FROZEN
  frozen: false

# 设计决策记录。决策演变通过 superseded 保留，不允许删除历史决策。
decisions: []
# 单条决策格式：
#  - id: D-001                # 决策 ID，D-三位数字，按序递增不复用
#    category: layout         # 类别：layout / navigation / visual-style / color / typography /
#                             #   density / component / interaction / chart / data /
#                             #   responsive / tech-constraint / acceptance / other
#    description: 页面采用单页面纵向布局   # 人读的决策描述
#    value: single-page       # 决策值（供机器读取，如 single-page / light-saas / comfortable）
#    status: confirmed        # proposed（AI 提议）| confirmed（用户确认）| pending（等待回答）| superseded（被替代）
#    source: user             # user（用户明确给出或确认）| ai（AI 建议，未经确认不得标 confirmed）
#    stage: DISCOVERY         # 该决策产生的阶段
#    superseded_by: D-005     # 仅 status 为 superseded 时必填，指向替代决策
#    confirmed_at: ""         # 用户确认时间（status 为 confirmed 时填写）

# 待确认问题池。问题解决后移入 history（question_resolved），不留在本列表。
pending: []
# 单条问题格式：
#  - id: Q-001                # 问题 ID，Q-三位数字，按序递增不复用
#    category: interaction    # 类别同 decisions
#    description: 是否需要问题详情抽屉
#    stage: INTERACTION       # 问题所属阶段
#    related_decisions: []    # 关联的决策 ID，供回退时检查影响面

# 修改历史，只追加不修改。按时间顺序记录所有关键动作。
history: []
# 单条历史格式：
#  - at: ""                   # 记录时间
#    action: decision_confirmed   # 动作，只允许：
#                             #   decision_proposed / decision_confirmed / decision_superseded /
#                             #   question_added / question_resolved /
#                             #   stage_advanced / design_generated /
#                             #   validation_passed / validation_failed /
#                             #   frozen / unfrozen / session_resumed / note
#    detail: ""               # 详情（涉及的对象 ID、回退目标阶段等）

# 产物状态
artifact:
  design_md_generated: false   # design.md 是否已生成
  design_md_path: design.md    # 生成路径（相对目标项目根目录）
  last_validation: ""          # 最近一次完整性检查结果：READY_FOR_REVIEW / FAILED / 空
---

# 会话记录

> 本 frontmatter 由 ui-design 工作流维护，校验标准见 schemas/design-session.schema.json。
> 写入规则：修改设计先更新本文件再更新 design.md；决策只增不删，被替代的标 superseded；
> history 只追加不修改；冻结与解冻必须由用户在对话中明确确认后执行。
