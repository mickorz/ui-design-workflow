# Dashboard 案例手动填充验证记录

- 日期：2026-11-11
- 目的：执行计划第 11 节第 3 步——用 Dashboard 案例手动填充 templates/ 模板，在编写 SKILL.md（T3）之前验证文档标准是否真的够用
- 产物：examples/dashboard/ 三件套（input.md、design-session.md、design-session 期望冻结态、design.md 期望交付态）

## 验证方式

1. 以 input.md 的模糊需求为起点，模拟 ui-design 完整走完七阶段
2. 输入中已明确的要求（受众、禁止项、布局、板块、风格、密度、数据源、HTML 目标）直接登记为 confirmed，不重复提问
3. 有意设计一次「后期修改早期决策」：INTERACTION 阶段确认的 D-009（行内展开）在 S7 被用户推翻，由 D-011（悬浮提示）替代，走 影响分析 → 重新生成 → 复检 → 冻结 的完整回路
4. 机器校验：session 过 Schema；design.md 13 章全 confirmed；第 13 章决策表与 session 逐 ID 对账；冻结态 pending 必须为空

## 结论：模板结构成立

- 13 个章节无空置、无强凑，dashboard 场景下每章都有实质内容
- 第 13 章决策表与 session 完全对账，决策追溯闭环成立
- 冻结态一致性（frozen=true ⇔ stage=FROZEN ⇔ pending 空）可被 Schema 与脚本共同保证

## 手动填充暴露的问题（T3 必须吸收）

| # | 问题 | 对 T3 的输入 |
|---|---|---|
| 1 | 第 6 章（组件定义）与第 8 章（交互设计）边界易混，同一组件可能两处都写行为 | SKILL.md 明确划界规则：第 6 章定「有什么」，第 8 章定「怎么反应」；组件的交互行为只写第 8 章 |
| 2 | 「数据范围/更新频率/是否可筛选」这类问题容易漏问，但它直接决定交互复杂度 | discovery.md 的问题清单中加入数据范围三问：范围、更新频率、是否需要筛选 |
| 3 | 决策 value 是自由文本时机器不可靠（如模块清单写成数组还是逗号串） | SKILL.md 附决策词表：category 固定枚举 + 常用 value 词汇；复合值用 YAML 列表 |
| 4 | S7 用户修改早期决策时，影响范围需要快速定位 | design-review.md 给出影响分析步骤：按决策 category → 受影响章节映射表 |
| 5 | 冻结前 pending 必须清空，但用户跳答时会遗留问题 | SKILL.md 规定：进入 S7 前逐条处理 pending（解决或经用户明确放弃），不得带未决问题冻结 |

## 对模板的回写

本次未修改 templates/。上述问题全部属于「执行规则」层面，通过 SKILL.md 与 references 落实，模板本身不需要改。
