# 角色目录

审查者角色被组织成一个小核心加上通用、横切和堆栈特定的条件。您（协调者）使用此目录仅选择其域存在于差异中的审查者。

## 核心和标准门

每次多代理审查都会产生正确性。仅当第 3b 阶段（发现项目标准路径）找到至少一个适用的标准文件，或者标准发现失败并且审查必须运行角色而不是默默地跳过它时，才会生成项目标准。

**结构化角色提示资产：**

| 人格面具 | 提示资产 | 重点 |
|---------|-------|-------|
| `correctness` | `correctness-reviewer` | 逻辑错误、边缘情况、状态错误、错误传播、意图合规性 |
| `project-standards` | `project-standards-reviewer` | 遵守逐条引用的项目指定标准文件 |

## 通用条件

这些审查者具有广泛的适用性，但并不一定有用。仅当它所检查的具体表面存在于差异中时才生成一个。

| 角色/资产 | 提示资产 | 当 diff 接触时选择... |
|---------|-------|-------|
| `testing` | `testing-reviewer` | 测试文件、测试基础设施、固定装置、模拟或利用行为；或有意义的运行时行为发生变化而没有相应的测试工作。行为触发器包括新的或更改的分支、状态突变、API/control-flow行为和错误处理。单独的生产文件存在和非行为编辑不会选择它。 |
| `maintainability` | `maintainability-reviewer` | 大型或结构性工作：大量重构、新抽象、文件移动、coupling/type-boundary 更改或至少 200 个可执行的更改行。 |
| `agent-native` | `agent-native-reviewer` | 面向代理的产品表面：差异更改代理工具表面（MCP 工具、代理工具或功能定义、系统提示构造），或者在已有此类表面的产品中添加或更改面向用户的功能。仅编辑技能、代理定义或说明文件的散文不会选择它。 |
| `learnings` | `learnings-researcher` | 该更改具有需要检查的制度知识：现有的 `<root>/solutions/` 语料库对于已更改的模块或模式具有合理的 path/title 匹配（首先运行廉价搜索；仅语料库存在不会选择它），或者，在本地范围内，存储库的 CE 配置声明Compound Pack（阶段 1b `declared_packs`，`references/scope.md` 中的语义）。声明的包无需预先搜索即可选择它；角色与每个规则的 `applies_when` 本身相匹配。 |

## 有条件（7 个角色）

当您在差异中识别出相关模式时，会生成其中之一。阅读完整的差异和选择原因——这是代理判断，而不是关键字匹配。

| 人格面具 | 代理人 | 当 diff 接触时选择... |
|---------|-------|---------------------------|
| `security` | `security-reviewer` | 身份验证中间件、公共端点、用户输入处理、权限检查（包括控制功能是否可访问的功能标志或权利门）、机密管理 |
| `performance` | `performance-reviewer` | 具体的性能敏感行为：database/ORM查询形状、算法复杂性、大型循环密集型转换、batching/fan-out或具有物质资源影响的缓存策略。当 correctness/reliability 已经拥有更改的语义时，Async/concurrent 代码或缓存数据结构不会单独选择它。 |
| `api-contract` | `api-contract-reviewer` | 外部使用的边界更改：route/request/response定义、序列化器、已发布的事件模式、API版本控制或具有证据的下游调用者的公共包签名。一个模块内的新的或更改的导出符号本身是不够的。 |
| `data-migration` | `data-migration-reviewer` | 迁移文件、模式转储（`db/schema.rb`、`structure.sql`）、回填脚本、数据转换 — **不是** model/query-only 没有迁移产物的更改 |
| `reliability` | `reliability-reviewer` | 错误处理、重试逻辑、断路器、超时、后台作业、异步处理程序、运行状况检查 |
| `adversarial` | `adversarial-reviewer` 后备 | `references/modes-and-output.md`中的对抗性选择条件适用：明确的用户请求或具有重大后果的明显失败场景，包括可以隐藏它的验证机制。当受制裁的对等点启动时，镜头会穿过独立的跨模型对等点。当对等方无法启动时、当折叠运行未运行的回退时或当折叠在失败的同路由速率限制重试后恢复本地时，生成此进程内角色。生成评审产物的启动同行和后备是相互排斥的。 |
| `previous-comments` | `previous-comments-reviewer` | **仅限PR且受评论限制。** 审阅具有现有审阅评论或来自先前审阅轮次的审阅线程的PR。当阶段 1 中没有收集到 PR 元数据时，或者当阶段 1 的 `hasPriorComments` 标志为 false（PR 上没有 `reviews` 和`comments`）时，完全跳过。 |

## 堆栈特定条件（1 个角色）

这些审查者涵盖专门的运行时行为。结构和可维护性问题属于条件 `maintainability` 角色 - 不会为哲学或仅约定通行证产生额外的堆栈审查者。

| 人格面具 | 代理人 | 当 diff 接触时选择... |
|---------|-------|---------------------------|
| `frontend-races` | `frontend-races-reviewer` | 任何框架（React、Turbo/Stimulus、纯 DOM 或其他）中的浏览器 UI 代码，其更改的行为可能会出现竞争：更新 UI 状态的异步获取或轮询、计时器或动画循环、事件侦听器、组件或控制器生命周期和清理，或者可能重叠的交互 |

## CE 有条件本地提示资产（特定于迁移）

当迁移产物条件（下面的选择规则 5）适用**并且**更改有风险（破坏性 DDL、回填、无默认值的 NOT NULL、列 renames/drops）时，请使用 `deployment-verification-agent`。模式漂移和迁移安全属于 `data-migration` 角色——而不是单独的类型代理。

| 提示资产 | 重点 |
|-------|-------|
| `deployment-verification-agent` | Go/No-Go 包含 SQL 验证查询和回滚过程的部署清单 |

## 评选规则

1. **始终生成正确性。** 仅针对非空适用标准路径列表生成项目标准；在成功的空搜索时跳过它，并在发现不确定时生成它，因此错误永远不会成为无提示的跳过。
2. **对于每个通用条件**，需要其显式表面。对于 `testing`，该表面已更改 tests/harnesses 或具体有意义的运行时行为，但没有相应的测试工作；仅存在生产文件是不够的。缺席意味着跳过，而不是“以防万一就跑”。
3. **对于每个横切条件角色**，阅读差异并确定其域是否相关。这是一个判断调用，而不是关键字匹配。
4. **对于每个特定于堆栈的条件角色**，使用文件类型和更改的模式作为起点，然后确定差异是否实际上为该审查者引入了有意义的工作。不要仅仅因为一个配置或生成的文件恰好与扩展名匹配就产生特定于语言的审查者。
5. **对于 `data-migration`**，仅当差异包含迁移或架构产物（`db/migrate/*`、`db/schema.rb`、`db/structure.sql`、Alembic/Flyway/Liquibase 路径或显式 backfill/data-transform 脚本）时才生成。如果没有这些文件，**不要**生成仅模型或仅查询的更改。
6. **对于 CE 条件提示资产**，当迁移产物条件适用并且更改有风险时（请参见上文），请使用 `deployment-verification-agent`。
7. **在生成之前宣布团队**，并为每个选定的条件审核者提供一行理由。
