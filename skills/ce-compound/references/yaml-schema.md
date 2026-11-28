# YAML Frontmatter 架构

该目录中的`schema.yaml`是`ce-compound`编写的`<root>/solutions/`frontmatter的规范合约。

使用此文件作为以下内容的快速参考：
- 必填字段
- 枚举值和开放词汇默认值
- 验证期望
- 类别映射
- 跟踪分类（错误与知识）

## 语料库第一词汇

`component`和`root_cause`是开放词汇表，类别目录是默认布局，不是固定的。已经保存学习内容的存储库通常有自己一致的值和目录名称，并且它们的检索（代理指令、greps、工具）是基于这些值和目录名称的。写入此文件默认值而不是存储库词汇表的文档是存储库无法找到的文档，这违背了编写它的意义。

因此，在分类之前：当 `<root>/solutions/` 已经包含文档时，采样该区域的 frontmatter (`component`、`root_cause`、`problem_type`、`tags`) 和目录名称。对于 `component`，使用语料库现有文档用于该区域的值（此更改所属的 component/directory 分组）。对于 `root_cause`，按原因本身而不是区域进行匹配：使用现有文档用于同一根本原因的值，无论这些文档位于语料库中的何处 — 区域的典型 root_cause 不会延续到已验证原因不同的文档。对于任一字段，当语料库对同一区域（组件）或同一原因 (root_cause) 有多个拼写时，请使用文档使用最多的拼写（领带：最近日期的文档）；仅当没有现有文档涵盖该区域（组件）或命名原因时（root_cause），才使用架构建议的默认值。按拼写重复使用语料库值 - 不要创造语料库已使用的值的近同义词。目录选择是一个单独的条件：将文档归档到涵盖该区域的现有目录中；仅当没有现有目录覆盖时才使用下面的类别映射。 `problem_type`、`severity`和`resolution_type`保持封闭枚举（`problem_type`驱动轨道选择）。

## 曲目

`problem_type` 确定适用哪个 **轨道**。每个轨道都有不同的必填字段和可选字段。

| 追踪 | problem_types | 描述 |
|-------|--------------|-------------|
| **漏洞** | `build_error`, `test_failure`, `runtime_error`, `performance_issue`, `database_issue`, `security_issue`, `ui_bug`, `integration_issue`, `logic_error` | 已诊断并修复的缺陷和故障 |
| **知识** | `best_practice`, `documentation_gap`, `workflow_issue`, `developer_experience`, `architecture_pattern`, `design_pattern`, `tooling_decision`, `convention` | 实践、模式、约定、决策、工作流程改进和文档。优先选择最窄的适用值； `best_practice` 是后备。 |

## 必填字段（两个轨道）

- **模块**：受影响的模块或区域
- **日期**：ISO 日期，格式为 `YYYY-MM-DD`
- **problem_type**：上面“轨道”表中列出的值之一
- **组件**：涉及的组件或领域——开放词汇（参见语料库-第一词汇）。当语料库没有该区域的值时建议的默认值：`data_model`、`api_layer`、`service_layer`、`background_job`、`database`、`frontend`、`messaging`、`infrastructure`、`observability`、`authentication`、`payments`、 `development_workflow`、`testing_framework`、`documentation`、`tooling`
- **严重性**：`critical`、`high`、`medium`、`low` 之一

## 错误跟踪字段

必需的：
- **症状**：YAML 数组，具有 1-5 个可观察到的症状（错误、损坏的行为）
- **root_cause**：基本技术原因——开放词汇（参见语料库-第一词汇）。建议默认值：`wrong_api`、`data_integrity`、`concurrency`、`async_timing`、`memory_leak`、`config_error`、`logic_error`、`test_isolation`、`missing_validation`、`missing_permission`、`missing_workflow_step`、`inadequate_documentation`、 `missing_tooling`、`incomplete_setup`
- **resolution_type**：`code_fix`、`migration`、`config_change`、`test_fix`、`dependency_update`、`environment_setup`、`workflow_improvement`、`documentation_update`、`tooling_addition`、`seed_data_update` 之一

## 知识领域

除了共享字段之外，没有其他必填字段。以下所有字段都是可选的：

- **applies_when**：本指南适用的条件或情况
- **症状**：导致本指南的可观察到的差距或摩擦
- **root_cause**：根本原因（如果有特定原因）
- **resolution_type**：变更类型（如果适用）

## 可选字段（两个轨道）

- **related_components**：涉及的其他组件
- **标签**：搜索关键字，小写且连字符分隔
- **retire_when**：存储库外部的更改将取消此学习，以及刷新如何在不更改存储库的情况下检查它。仅当指南成立且存储库外部的某些内容成立时才设置它：开放的上游错误、工具或平台版本、依赖项的行为。否则省略它。需要更改存储库的验证（例如删除解决方法并重新运行 CI）属于删除之前的步骤。它是一根弦；当包含 ` #` 或 `: ` 时，引用整个值。

## 可选字段（仅限错误跟踪）

- **framework_version**：观察到错误的框架或运行时名称和版本，例如`rails 7.1.2` 或 `node 22.4.0`

## 向后兼容性

在跟踪系统之前创建的文档在知识类型problem_types上可能有`symptoms`/`root_cause`/`resolution_type`。这些是有效的遗留文档：

- 知识跟踪文档中出现的错误跟踪字段是无害的。除非文档因其他原因被重写，否则请勿在刷新期间删除它们。
- 在 `component`/`root_cause` 成为开放词汇之前编写的文档可能会携带来自早期封闭列表或早期 `rails_version` 字段（现在为 `framework_version`）的值。它们保持有效，并且持续使用它们的语料库会继续使用它们。
- 创建**新**文档时，请遵循上面的跟踪规则。

## 类别映射

没有现有学习内容的存储库的默认布局。当 `<root>/solutions/` 已经建立了目录分类法时，请将文档放置在覆盖该区域的现有目录中（上面的语料库优先规则），而不是从此表创建一个没有其他内容使用的新目录。

- `build_error` -> `<root>/solutions/build-errors/`
- `test_failure` -> `<root>/solutions/test-failures/`
- `runtime_error` -> `<root>/solutions/runtime-errors/`
- `performance_issue` -> `<root>/solutions/performance-issues/`
- `database_issue` -> `<root>/solutions/database-issues/`
- `security_issue` -> `<root>/solutions/security-issues/`
- `ui_bug` -> `<root>/solutions/ui-bugs/`
- `integration_issue` -> `<root>/solutions/integration-issues/`
- `logic_error` -> `<root>/solutions/logic-errors/`
- `developer_experience` -> `<root>/solutions/developer-experience/`
- `workflow_issue` -> `<root>/solutions/workflow-issues/`
- `best_practice` -> `<root>/solutions/best-practices/`
- `documentation_gap` -> `<root>/solutions/documentation-gaps/`
- `architecture_pattern` -> `<root>/solutions/architecture-patterns/`
- `design_pattern` -> `<root>/solutions/design-patterns/`
- `tooling_decision` -> `<root>/solutions/tooling-decisions/`
- `convention` -> `<root>/solutions/conventions/`

## 验证规则

1. 使用轨迹表确定从 `problem_type` 开始的轨迹。
2. 所有共享必填字段都必须存在。
3. 错误跟踪必填字段（`symptoms`、`root_cause`、`resolution_type`）必须出现在错误跟踪文档中。
4. 除了共享字段之外，知识轨道文档没有其他必填字段。
5. 现有知识跟踪文档上的错误跟踪字段是无害的（请参阅向后兼容性）。
6. 枚举字段（`problem_type`、`severity`、`resolution_type`）必须与允许的值完全匹配。
7. 开放词汇字段（`component`、`root_cause`）遵循上述语料库优先词汇规则。
8. 数组字段必须遵守 min/max 项目计数。
9. `date` 必须匹配`YYYY-MM-DD`。
10. `framework_version`，如果存在，仅适用于错误跟踪文档。
11. `retire_when` 在两个轨道上都是可选的。当存在时，它是一个字符串，没有它的文档仍然有效。

## YAML 安全规则

严格 YAML 1.2 解析器（`yq`、`js-yaml` strict、PyYAML）拒绝以保留指示符字符开头的数组项作为不带引号的标量。为任何字符串数组字段（`symptoms`、`applies_when`、`tags`、`related_components`或任何未来的数组字段）编写项目时，如果值以以下任一开头，请将值括在双引号中：

`` ` ``, `[`, `*`, `&`, `!`, `|`, `>`, `%`, `@`, `?`

如果该值包含子字符串 `": "`，则还要引用——该标点符号会使流式解析器感到困惑。

示例 — 之前（违反严格 YAML）：

    症状：
      - `sudo dscacheutil -flushcache` 不恢复容器内 mDNS

示例 - 之后（干净地解析）：

    症状：
      - “`sudo dscacheutil -flushcache` 不恢复容器内 mDNS”

此规则适用于所有字符串数组 frontmatter 字段。像 `description:` 这样的标量字符串字段有自己的引用规则（请参阅“YAML Frontmatter”下的插件 `AGENTS.md`）。
