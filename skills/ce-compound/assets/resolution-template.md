# 分辨率模板

选择与problem_type轨道匹配的模板（参见`references/schema.yaml`）。

---

## 错误跟踪模板

用于：`build_error`、`test_failure`、`runtime_error`、`performance_issue`、`database_issue`、`security_issue`、`ui_bug`、`integration_issue`、`logic_error`

<!-- YAML safety: array items (symptoms, applies_when, tags, related_components) starting with ` [ * & ! | > % @ ? or containing ": " must be wrapped in double quotes. See references/yaml-schema.md > "YAML Safety Rules". -->

```markdown
---
title: [清除问题标题]
日期：[年-月-日]
类别：[解决方案子目录]
模块：[模块或区域]
problem_type：[架构枚举]
组件：[语料库值，否则架构建议默认]
症状：
  - [观察到的症状1]
root_cause：[语料库值，其他模式建议默认]
resolution_type：[架构枚举]
严重性：[架构枚举]
retire_when：[可选；将使该文档失效的外部更改以及如何检查它，否则忽略此行]
标签：[关键字一，关键字二]
---

# 【明确问题标题】

## 问题
[1-2 句话描述问题和用户可见的影响]

## 症状
- [观察到的症状或错误]

## 什么不起作用
- [尝试修复以及失败原因]

## 解决方案
[有效的修复，包括有用的代码片段]

## 为什么这有效
[根本原因解释以及修复解决该问题的原因]

## 预防
- 【具体实践，测试，还是护栏】

## 相关问题
- [相关文档或问题，如果有的话]
```

---

## 知识轨道模板

用于：`best_practice`、`documentation_gap`、`workflow_issue`、`developer_experience`、`architecture_pattern`、`design_pattern`、`tooling_decision`、`convention`

<!-- YAML safety: array items (symptoms, applies_when, tags, related_components) starting with ` [ * & ! | > % @ ? or containing ": " must be wrapped in double quotes. See references/yaml-schema.md > "YAML Safety Rules". -->

```markdown
---
标题：[清晰的描述性标题]
日期：[年-月-日]
类别：[解决方案子目录]
模块：[模块或区域]
problem_type：[架构枚举]
组件：[语料库值，否则架构建议默认]
严重性：[架构枚举]
applies_when:
  - [适用条件]
retire_when：[可选；将使该文档失效的外部更改以及如何检查它，否则忽略此行]
标签：[关键字一，关键字二]
---

# [清晰、描述性的标题]

## 语境
[什么情况、差距或摩擦促使了本指导]

## 指导
[有用的实践、模式或建议以及代码示例]

## 为什么这很重要
[遵循或不遵循本指南的理由和影响]

## 何时申请
- [适用的条件或情况]

## 示例
[具体before/after或展示实际实践的使用示例]

## Related
- [相关文档或问题，如果有的话]
```
