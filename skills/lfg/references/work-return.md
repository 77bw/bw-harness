# 读取 ce-work 的结构化回报（LFG 步骤 2）

LFG 的 SKILL.md 仅允许有效的 `status: complete` 返回预付款；所有其他状态或格式错误的返回都会停止管道。该文件定义了如何验证完整的返回：路由绑定的含义、需要哪些字段、验证证据必须包含什么以及一次恢复调用。

## 失踪业主阻止退货

当`ce-work`在创建了部分状态后无法重新读取定义其返回的参考文件时，它会从其SKILL.md返回一个减少的阻塞结果。接受减少的结果作为有效的终端阻塞项，而不是格式错误的完整返回。它包含 `status: blocked`、`plan_path`、`run_id`（已知）、`changed_state`、`blockers` 和 `recovery_path`。保留这些恢复事实并停止；下面的完整返回现场清单不适用于此故障形状。

## 每条路线的结果意味着什么

`ce-work`公开了一次不可用的路由，并在`prefer`和`require`下继续本机地继续（其`cross-model-execution.md`定义了该行为），因此LFG根据返回字段决定路由结果，而不是期望`ce-work`拒绝。 `implementation_engine_binding.mode`为`require`且`actual_route`与`requested_route`不同的返回将管道停止为阻塞，报告`requested_route`、`actual_route`和`fallback_reason`； `require` 是调用者的指令，并且本机根据它完成的工作不会传送。已完成的`prefer`回退可以在向用户显着地披露其请求与实际route/model和`fallback_reason`之后继续执行步骤3；回退并不是再次调用实现的理由。

## `status: complete`必须携带什么

验证实施工作是否已执行：文件的创建或修改超出了计划。需要 `status`、`plan_path`、`changed_files`、`u_ids_attempted`、`u_ids_completed`、`verification_results`、`verification_evidence`、`source_kind`、`source_digest`、`settled_decision_conflicts`、`behavior_change` 和 `standalone_shipping_skipped: true`。源字段必须标识进入实施运行的同一计划机构。 `source_digest` 是控制器记录的摘要，或者在本机运行时为 null。在一次性语句中，`plan_path`为空，`source_kind`为`prompt`，`u_ids_attempted`和`u_ids_completed`为空数组。恢复调用会重复该语句而不改变计划路径。每一份完整的回报中都会出现证据和冲突字段；当条件未发生时，空数组有效。

还需要记录实际运行路线的字段：`implementation_engine_binding`、`requested_route`、`actual_route`、`requested_model`、`actual_model`、`fallback_reason`、`run_id`、`unit_receipts`、`plan_checkpoint`、`blockers` 和 `recovery_path`。即使本机执行使某些值`null` 时，这些字段也是必需的。它们一起承载了绑定的来源、请求的身份与实际的身份、回退、持久运行、每单元 process/integration/verification/commit 状态、检查点披露、阻塞项和恢复。恢复的退货必须携带相同的`run_id`；切勿将简历视为启动新装置或第二次垃圾填埋气运输的许可。

## 工作必须全力以赴

`ce-code-review` 遗漏了未跟踪的文件，因此此运行添加的文件在提交之前不会进行审核。在步骤 3 之前，确认退货的 `changed_files` 已提交。如果没有，请提交这些文件并继续。不要为此停下来。

## 验证证据

当`behavior_change: true`、`verification_evidence`必须命名相关units/tasks、已检查的现有测试、测试added/changed或未更改使用、红色故障或特性证据（适用时）、验证运行以及任何故意的测试异常。不要在 LFG 内部决定测试策略；证据就是ce-work的合同。

还从返回中读取`settled_decision_conflicts`：阻塞路由条目以`status: blocked`到达并停止管道。 **记录任何已处理和标记的条目**：它们必须达到步骤 6 的未应用结果的持久记录和步骤 9 的 PR 描述上下文，因为以后的审查可能不会重新发现它们。

## 一次恢复调用

如果 `behavior_change: true` 但 `verification_evidence` 丢失或太模糊而无法说明如何保护行为，请在恢复模式下再次调用 `ce-work`。当存在相同的`implementation_engine:<compact-json>`载体时，重复使用该载体并保持相同的计划路径。使用安全的非空 `run_id`，将 `implementation_run:<safe-id>` 添加到第一次返回的确切值。当`actual_route`为`native`且`run_id`为`null`时，重复原始ce-work调用一次，无需`implementation_run:`载体；这保留了预先存在的本机 idempotency/evidence-reconciliation 路径。没有安全运行 ID 的非本机返回仍会被阻止，而不是尝试发现或第二次实现。不提示用户，也不改变计划路径或发动机托架；这是证据和解，而不是新的派遣。恢复依靠ce-work的协调路径来检查已经实施的工作，填补缺失的证据，然后返回而不重新实施。如果第二次返回仍然缺乏连贯的验证证据，则停止并报告缺失的字段，而不是继续simplify/review/ship。
