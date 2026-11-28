# 参数、模式和可交付成果

在解决范围之前，请在第 0 阶段阅读此内容。它定义了如何解析参数、哪些参数组合会停止审阅、快速审阅短路以及每种模式返回的内容。

为您读取的每个文件提供自己的工具调用，以便其输出自行返回，而不是在一个命令或一个脚本中返回多个文件。仅当整个文件返回时，读取才算数。某些主机会从长工具输出中切掉中间部分，并在其位置留下截断标记，因此当读取返回时缩短，请在对该文件进行操作之前读取较小范围内的缺失行。这适用于您在审阅期间阅读的每个文件，而不仅仅是引用文档。

## 参数解析

解析您调用的参数以获取可选标记。在将剩余部分解释为 PR 数字、GitHub URL 或分支名称之前，先剥离每个已识别的标记。

| 代币 | 例子 | 影响 |
|-------|---------|--------|
| `mode:agent` | `mode:agent` | **仅报告**：返回 **JSON** 而不是 Markdown 表并跳过阶段 5c 应用（调用者应用）。不更改审查者选择、合并逻辑或范围规则（请参阅输出格式） |
| `mode:headless` | `mode:headless` | **已弃用 `mode:agent` 的别名** |
| `mode:report-only` | `mode:report-only` | **已弃用 — 已忽略。** 以前的无产物模式；默认行为是仅审核而不结帐 |
| `apply:local` | `apply:local` | 明确授权 Stage 5c 将经过验证的结果应用于经过审查的本地结账。这是权威，不是输出方式；纯粹的审查仍然只是报告。 |
| `base:<sha-or-ref>` | `base:abc1234` 或 `base:origin/main` | 基于 **当前结账** 进行差异基础（显式；跳过自动基础检测） |
| `plan:<path>` | `plan:<root>/plans/2026-03-25-001-feat-foo-plan.md` | 需求验证的计划文件（显式）。支持markdown和HTML统一方案。 |
| `plan_group:<label>` | `plan_group:PR2` | 对于`plan:`，此差异构建的多PR计划的PR组，由开始其标题的标签命名（`PR2: Report headline and summary`中的`PR2`）。范围计划对该组的完整性（参见`references/intent-and-plan.md`）。 |
| `depth:full` | `depth:full` | **强制整个脊柱** — 跳过查看深度门的精简路径和集中路径。当明确请求 deep/thorough 审查时使用（覆盖门的审查无法推断）。不更改完整路径上的条件选择、合并或范围。 |
| `depth:auto` | `depth:auto` | **默认** — 此技能在第 1 阶段之后通过复习深度门自行调整大小。调用者不会进行分类。 |
| `grouping:auto` | `grouping:auto` | **默认** — 当调查结果涵盖不同的问题时建立主题分类组（第 5 阶段步骤 9b） |
| `grouping:off` | `grouping:off` | 抑制分类组：无分类组部分，JSON 中为空 `triage_groups` |
| `grouping:always` | `grouping:always` | 始终建立分类小组，即使是小评论 |

**分组是表示形式，而不是模式。** `grouping:` 标记会改变结果集的分类组织方式 — 绝不是审查者选择、合并逻辑、范围规则或第 5c 阶段应用决策。

**模式别名：** `mode:headless` 标准化为 `mode:agent`。 `mode:agent` + `mode:headless` 不冲突。 `mode:non-interactive` **不是** `mode:agent` 的别名 — 该标记在其他 CE 技能中表示“抑制提示”；如果它出现在这里，请将其视为无法识别的、冲突的 `mode:` 标记并停止，而不是猜测其含义。

**冲突的论点：** 在以下情况下停止而不派遣审稿人：
- 多个不兼容的范围选择器一起出现（例如 `base:` **和** PR number/branch 目标 — `base:` 表示“根据此基础查看当前结账”）
- 除 `mode:agent`/`mode:headless` 别名对之外的多个不同的 `mode:` 标记
- `mode:non-interactive`（单独或与其他模式一起）—对该技能无效；使用`mode:agent`代替JSON
- `apply:local` 与 `mode:agent` 一起 — 管道切换始终仅报告
- 多个不同的 `grouping:` 标记（例如 `grouping:off` ** 和 ** `grouping:always`）

已弃用的 `mode:autofix` **不是** 冲突 - 忽略该令牌并继续正常流程（见下文）。

发出一行失败原因。在`mode:agent`中，返回JSON：`{"status":"failed","reason":"..."}`。

## 输出格式

| 祈求 | 可交付成果 |
|------------|-------------|
| **默认** | 仅报告Markdown（以竖线分隔的结果表）+ 可操作的结果摘要 |
| **显式本地应用** | 相同的Markdown报告加上经过验证的本地修复和应用部分 |
| **`mode:agent`** | 一个 JSON 对象（请参阅下面的 ## JSON 输出格式）+ 相同的 `/tmp/.../ce-code-review/<run-id>/` 产物 |

默认值和`mode:agent`是**仅报告**。对于编程调用者，`mode:agent` 仅将序列化从 markdown 更改为 JSON；它不会更改审查者选择、合并逻辑或范围规则。 `apply:local`是单独的变异权限，不是输出模式。默认的 Markdown 是人类视图；保持它的 ASCII 安全（管道表，`->`不是中点`·`，没有方框图），这样它就可以在终端之间优雅地降级。

无论该技能返回什么，包括失败、降级或跳过的结果，都是它写入的最后内容。它结束了该技能，而不是回合。当调用者调用此技能时，控制权将在同一会话中返回给调用者，并且调用者自己对结果的处理决定其运行是继续还是停止；否则结束回合。

## 快速回顾短路

如果调用参数表明用户想要快速、快速或轻松的代码审查 — 并且 **`mode:agent` 未激活** — 不要分派多代理流。

**在任何其他工作之前宣布所选路径**（快速审查与多代理审查）。当`mode:agent`激活时跳过此公告。

顺序：

1. **运行工具的内置代码审查。** 剥离令牌后转发任何审查目标。然后停止——不调度多代理管道。
2. **豁免：** 如果不存在内置审核，则继续进行完整的多代理审核。
3. **`mode:agent` 仅绕过此短路。** 它仍然通过审查深度门自行调整大小，并从该门选择的任何路径返回 JSON。

**已弃用：** 不再支持 `mode:autofix`。如果通过，则忽略它并仅进行报告；它不授予本地申请权限。

## 复习深度

在阅读任何后续引用文档之前，请在第 1 阶段（其 1b 事实和 1c 映射）之后做出决定。这个技能拥有决定权；调用者可能会传递 `depth:full` 但永远不会传递其自己的深度。存在三种路径：**lite**（仅此上下文）、**focused**（此上下文加上一个独立的对抗性读取）和 **full**（来自第 2 阶段的多代理主干）。

从第 2 阶段开始贯穿整个脊柱的楼层，无论差异如何：`depth:full`；助手的`hard_block_full`（助手报告事实。它从不奖励精简版。`hard_block_full`是一个楼层，它涵盖了一个命名的硬块类，助手无法计数的任何文件，以及`large`的`size_band`，这意味着可执行的非测试更改行达到了整个楼层；整个文件删除不计入其中）；失败或范围不确定的 1c 阶段标准检索；并申请权限（`apply:local`或明确的申请请求），这需要阶段5c的验证申请机制。楼层以下的行数、散文和测试卷、`unclassified_lines`和`signals`是需要考虑的提示，而不是楼层。

### 对抗性选择

当用户明确请求时选择对抗性镜头。否则，选择需要来自可信故障场景的差异和可用上下文的证据，并产生重大后果：未经授权的访问或披露、财务损失、持续的数据损坏或丢失、不可逆转的外部影响或严重的服务中断。说明该场景和后果作为选择原因。验证机制继承了它所保护的行为的后果；仅仅虚假的成功是不够的。

差异大小、文件路径、域关键字、常规持久性或 API 使用以及不确定性本身并不能选择对抗性。当证据支持重大后果时，未解决的风险仍然值得关注，即使其可达性需要调查。否则，请在覆盖范围中记录特定的不确定性，而不是添加审查者以防万一。此条件适用于重点审查和全面审查。

如果没有完整的脊柱地板设置，则在不存在对抗条件时选择精简版。如果存在，请选择“集中”，除非更改需要整个主干的专家覆盖授权、资金或外部使用的公共合同边界；然后从第二阶段继续。即使没有选择对抗性，这些专家边界仍然需要全面审查。用户提出的对抗性审查请求至少需要有针对性； `depth:full`单独不选择镜头。

助手的 `silent_pass_classes`、`deleted_band` 和 `unclassified_lines` 识别要检查的工作，而不是额外的深度楼层。评估更改后的防护措施保护的内容以及幸存的代码是否仍能到达已删除的文件。单独的CI路径或大删除不需要独立读取。无法识别的扩展名下的可执行代码仍然会收到相同的结果评估。

完整的脊柱地板不能被谈论下来，只有当新的证据出现时，一条道路才可能走向完整。总的来说，正确性仍然是强制性的，专家的选择仍然是有条件的；使用上面的对抗条件而不是从深度推断它。

当门选择精简或聚焦时，在该点读取`references/depth-paths.md`并从此上下文运行所选路径；完整的书脊从第 2 阶段继续，并且永远不会打开该文件。无论哪种方式，通过以下决定关闭范围阶段：来自`references/scope.md`的阶段日志调用带有`--end scope --start review`（精简版，重点）或`--end scope --start select`（完整），携带`exec_nontest_lines`，`changed_lines`，`size_band`，`deleted_band`，`unclassified_lines`的`--fact`条目，以及`depth`。

## 运行产物

每次运行，无论是精简版、集中版还是完整版，都会在运行目录中留下其收据（`mode:agent`中的`review.json`，默认模式中的`report.md`）、`stages.jsonl`（阶段日志`references/scope.md`打开）和`metadata.json`。 `metadata.json` 最小字段：

```json
{
  "run_id": "<run-id>",
  "branch": "<发送时的 git 分支 --show-current>",
  "head_sha": "<git rev-parse HEAD 在调度时>",
  "verdict": "<Ready to merge | Ready with fixes | Not ready>",
  "completed_at": "<ISO 8601 UTC timestamp>"
}
```

写入`metadata.json`后，收据写入器运行`run-log.py summarize --run-dir "$RUN_DIR"`（与阶段日志相同的`SKILL_DIR`和解释器配方）作为返回或发出收据之前的最后一个操作；它是唯一在收据写入后触及`metadata.json`的编写器，并将`cost`对象合并到现有字段中：`status`（当每个启动阶段结束且收据阶段存在时`complete`，否则`partial`），`host`，`scope`（辅助事实和从范围阶段选择的深度）， `stages`（名称、经过的秒数、审查者、候选项、令牌（如果存在））、`totals`（已过的、审查者、审阅、对等和分派阶段生成的候选项、产物字节、任何阶段携带它们时的令牌）、`peer`（来自`adversarial-<provider>-usage.json`（如果存在）和`truncated_events`。中途终止的运行会留下可解析的部分日志，并且维护者在信任运行数字之前调整`FULL_EXEC_LINE_MIN`或另一个阈值读取`cost.status`。

完整路径添加 `references/finish-input.md` 中“运行产物”下列出的产物。

## JSON 输出格式（仅限`mode:agent`）

所有深度共用同一输出协议。主响应只返回**一个原始 JSON 对象**，不加文字或代码围栏；否则直接调用 `JSON.parse` 的消费者会解析失败。把完全相同的载荷写到已解析的 `<run-dir>` 下的 `review.json`。

`mode:agent` 不应用修复（调用者应用），因此没有 `applied_fixes` 字段；切换是`actionable_findings`。应用的工作仅出现在明确授权的本地应用Markdown运行中（阶段5c/6）。

最小形状：

```json
{
  "status": "complete",
  "verdict": "Ready to merge | Ready with fixes | Not ready",
  "scope": {
    "base": "<merge-base sha, pr:NNN marker, or base: ref>",
    "branch": "<current branch name>",
    "head_sha": "<git rev-parse HEAD>",
    "pr_url": "<url or null>",
    "files_changed": 0
  },
  "intent": "<2-3 line summary>",
  "intent_confidence": "explicit | inferred | uncertain",
  "reviewers": ["correctness"],
  "findings": [],
  "actionable_findings": [],
  "triage_groups": [],
  "pre_existing_findings": [],
  "requirements_completeness": null,
  "learnings": [],
  "deployment_notes": [],
  "residual_risks": [],
  "testing_gaps": [],
  "coverage": {"depth": "lite | focused | full"},
  "artifact_path": "<resolved-run-dir>",
  "run_id": "<run-id>"
}
```

`peer` 告诉调用者不同提供商的同行是否实际审查了更改。它不是最小形状的一部分：仅当本次运行选择了对抗性镜头（完整名单选择了它，或聚焦路径运行）时才添加它，并且从不在精简版上添加它。其形状：

```json
"peer": {"outcome": "folded | in-process-fallback | not-run | no-usable-output | failed", "coverage": "<该结果的覆盖句子>"}
```

在完整路径上，从`finish-input.json`中的`peer`记录逐字复制`outcome`和`coverage`；聚焦路径使用相同的结果名称和覆盖句子从自己的折叠中填充它们。 `folded` 是同行产物被纳入本次审查的唯一结果。所有其他结果都意味着没有同行产物被折叠，而`coverage`说明了为什么以及什么覆盖了镜头。 `folded`以外的结果永远不会改变`status`。

当阶段 1d 上演审核策略时，每个路径都会添加 `coverage.review_policy`：`sources`（读取的策略文件路径）、`removed` 和 `regraded`（计数）以及 `not_applied`（更改编辑的策略文件，本次审核不应用其新版本）。

Lite 根据自己的评论填充了 `findings`、`actionable_findings`、`testing_gaps`、`residual_risks` 和 `requirements_completeness`（`null` 仅当未找到计划时）。未运行的审查者拥有的数组（`learnings`、`deployment_notes`、`pre_existing_findings`、`triage_groups`）为`[]`，Coverage 将它们命名为未评估。 `reviewers` 是`["correctness"]`，`coverage.depth` 是`"lite"`。 Focused 从合并的结果中填充相同的字段，列出其两位审稿人，并将 `coverage.depth` 设置为 `"focused"`；完整路径的完成叶填充每个字段并将 `coverage.depth` 设置为 `"full"`。

`findings` 中的每个对象都使用合并的查找字段：`#`、`title`、`severity`、`file`、`line`、`confidence`、`autofix_class`、`owner`、`requires_verification`、`pre_existing`、 `suggested_fix`、`first_evidence`、`why_it_matters`、`evidence`、`reviewers`、`independent_reviewers`。未解决的第 5b 阶段的发现，或因未测量的发生原因而得到确认的结果，也带有 `validation_status` 和 `validation_reason`，并且在申请时带有 `protected_subject`。 `learnings` 中的每个对象都是已知模式注释：`type` (`known_pattern`)、`title`、`citation`（`<root>/solutions/` 路径或`(pack: <id>, <包内的路径>)`）和 `note`（一行说明其如何影响更改）；矛盾的包规则是发现，而不是`learnings`条目。当Compound Pack被解析时，在任何路径上，`coverage.compound_packs`都会携带`roots`作为包ID列表（字符串 - 绝不是解析器的绝对`dir`路径）加上解析器的`warnings`和`errors`数组逐字，因此消费者可以告诉已声明的包是从跳过的包加载的。助手导出`independent_reviewers`；综合可以保留或联合该列表，但不得从 `reviewers` 推断它。

传入的结果可能带有一个可选的 `settled_conflict` 字段，命名为 `session-settled:` KTD。该标记为和解调节提供了背景；它并不免除承认或授权更改调查结果。

`actionable_findings` 列出了 `gated_auto` / `manual` + `downstream-resolver` 子集，具有相同的字段以及稳定的 `#`。 `validation_status: "unresolved"` 的发现从未出现在这里；它留在`findings`作为一个明确标记的验证门。

`triage_groups`中的每个对象都携带`{ "title", "findings": [<stable #s>], "context", "preferred_resolution", "why" }`：在阶段5b步骤5修剪之后阶段5步骤6的最终组。每个引用的`#`必须存在于`findings`（完整集）中，**不一定**一定存在于`actionable_findings`中。组是对所有结果进行分类**的镜头，而不是应用队列**：组（及其 `preferred_resolution` 顺序）可以参考调用者不得应用的建议或 `human`/`release` 拥有的结果。因此，按主题批处理相关修复的调用者必须首先将每个组的 `findings` 与 `actionable_findings` 相交，并仅对该子集执行操作；应用切换保持`actionable_findings`，而不是`triage_groups`。当 `grouping:off` 处于活动状态或未构建组时为空数组。

如果在审核完成之前失败，请设置 `"status": "failed"` 和 `"reason": "<one sentence>"`。当所有审查者都失败时，使用 `"status": "degraded"` 并给出原因。当 PR 跳过规则适用 (closed/merged/trivial) 时，请使用 `"status": "skipped"` 和跳过原因。当 `mode:agent` 处于活动状态时，不要发出Markdown表。

在完整路径的第 6 阶段之后，审核以可操作的摘要、运行产物和运行停止点结束。 `references/finish-report.md` 定义整个脊柱的结尾。
