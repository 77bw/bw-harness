# 返回呼叫者

当输入分类进入返回呼叫者模式时请阅读此内容。仅当其全文不再在上下文中（如压缩后）时，才在返回之前再次阅读它。输入分类拥有并验证调用语法（`references/input-triage.md`解析模式令牌和载体）。该文件定义了您返回的摘要的每个字段、`status: complete`的证据规则、重复运行如何在不重新实现的情况下恢复，以及您不能在此处执行的独立工作：简化、审查、PR、CI和PR 看护。

在此模式下，`ce-work`仅执行实施和本地验证 - 包括实施中期阶段 2“随行简化” - 然后返回结构化摘要，而不是运行独立的交付收尾（最终简化、审查、PR、CI）。它仍然按照第 2 阶段的指示对每个已完成的单元进行规范提交；调用者仅提交剩余的内容。一份工作声明算作一个单元，因此在返回之前提交它。当计划交付多个 PRs 时，无论如何都在一个分支上构建每个单元；调用者将工作分成PRs，因此`references/multi-pr-delivery.md`在这里不适用。摘要是该模式最后写的内容。它结束了该技能，而不是回合。调用者在同一个会话中运行，其下一步遵循摘要。

返回：

- `status`：`complete`、`blocked` 或 `failed`
- `plan_path`：计划的路径，或`null`用于工作说明。对于工作声明，请阅读本文件中的“计划”作为声明。
- `changed_files`
- `u_ids_attempted`
- `u_ids_completed`
- `verification_results`
- `verification_evidence`：每个尝试的行为承载单元一个条目，加上故意跳过测试的任何非行为单元。每个条目均说明unit/task、`behavior_changed`、`existing_tests_inspected`、`tests_added_or_changed`、未更改使用的测试、适用时观察到的红色故障或特征、验证commands/results以及任何异常原因。对于子代理执行的单元，此条目是根据每个工作人员返回的证据组装的，而不是根据差异重建的 - 实施前的红色观察仅存在于工作人员的报告中。
- `implementation_engine_binding`：在没有绑定的情况下选择本机执行时解析的一次性运行 `mode`、`target`、`model` 和 `source` 或 `null`
- `requested_route`和`actual_route`：目标加上harness/intermediary身份，在发生后备或同族替换时保持分开
- `requested_model` 和 `actual_model`：请求的模型和模型标识所提供的路线收据报告（`unverified` 当路线提供不可靠的收据时）
- `requested_effort`：为外部工作人员请求的推理工作，或者当没有请求或执行是本机时为`null`
- `fallback_reason`: `null` 无时，否则观察到的路线不可用或替换原因
- `run_id`：持久的外部运行标识符，或`null`用于本机执行
- `source_kind` 和 `source_digest`：控制器记录为实现源的内容（`plan` 加上其计划摘要；`prompt` 用于纯粹的提示或工作声明）
- `unit_receipts`：每个尝试单元的路由、模型、分离进程、集成、验证、规范提交和清理状态
- `plan_checkpoint`：当所选计划是唯一规范污垢时公开的检查点提交，否则`null`
- `blockers`：每个指定的拦截器，或者当没有剩余时为空列表。仅在指定阻塞项的每个范围内单元完成之前停止；完成的摄入量或进度点不是其中之一。
- `recovery_path`：当恢复仍然存在时，控制器保留并检查的run/workspace位置；否则`null`
- `settled_decision_conflicts`：与实施过程中遇到的`session-settled:`标记的 KTD 或关键决策冲突 - 每个条目命名标记的条目、证据及其路由方式（进行并标记与阻止）；当没有时为空
- `behavior_change`：行为承载代码是否改变
- `simplified_through`：仅当相边界`ce-simplify-code`通过运行时才出现；提交 SHA 覆盖了最新的传递，如 `references/implementation-loop.md` 所记录的那样。否则省略该字段。
- `standalone_shipping_skipped: true`

当选择本机执行而不进行绑定或后备时，路由字段仍然会出现，并具有固定值：`actual_route`是`native`； `implementation_engine_binding`、`requested_route`、`requested_model`、`requested_effort`、`fallback_reason`、`run_id`、`source_digest`、`unit_receipts` 和 `plan_checkpoint` 为 `null`。将它们写在一行中，无需解释。不要为此类运行计算摘要或构建收据；这些仅来自跨模型控制器。

仅当承载行为的工作有验证证据或故意例外时才返回`status: complete`。在返回之前，重新打开计划并根据差异重新检查其活动单元、验证合同和完成定义，因为上下文可能已被压缩为丢失细节的摘要。删除未成功的方法中留下的代码。如果先前的返回调用者运行实现了代码但省略了证据，则稍后的相同计划返回调用者运行应使用幂等性检查来检查现有工作、完成证据并返回而不重新实现。

引擎选择（`references/execution-engines.md`）在此模式下仍然适用，但仅用于实现。无论哪个引擎运行都不得打开 PR、运行独立的运输步骤或跳过调用者控制的检查。
