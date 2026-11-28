# 读取ce-debug的结构化回报（LFG缺陷路线）

在缺陷路线上，`ce-debug mode:return-to-caller`同时是工作源和实现：它重现、找出根本原因、按照测试优先原则进行修复、验证并在功能分支上提交而不推送。该文件定义了如何读取其返回值、返回提前值、后面的每个步骤用什么替换它将接收的计划路径，以及停止的一种情况。

## 有何进步

只有`status: fixed`前进到步骤3。`fixed`返回可能仍然携带`needs-human``residuals`，例如与`ce-debug`留下决策相同错误的另一个站点。他们继续进行修复，第 10 步用PR 看护的修复来渲染它们。 `diagnosed-no-fix`、`needs-human`和`blocked`停止运行，并逐字报告返回的`summary`、`root_cause`、`residuals`、阻塞程序和任何非空`prevention_signal`；没有任何东西被推动。格式错误的返回，或者 `fixed` 返回，其修复拥有的文件显示分支上没有任何更改，会因阻塞而停止运行。一个 `ce-debug` 运行在根本不发出返回值的情况下结束，即使它提交了修复，也是格式错误的：如果没有它的 `pre_fix_scope`，此运行中的任何内容都无法告诉该分支在修复之前持有什么。

## `status: fixed`必须携带什么

需要 `status`、`root_cause`、`changed_files`、`head_sha`、`branch`、`pre_fix_scope`、`verification_evidence`、`residuals`、`issue_of_record`、`behavior_change` 和 `standalone_shipping_skipped: true`。空数组在 `residuals` 内有效；当输入不带票据时，`issue_of_record`为`null`。此门不需要 `prevention_signal`：缺失或 `null` 值不会改变任何内容。非空值是对用户的建议，因此此运行中的任何步骤都不会实现它。

`verification_evidence`遵循相同的形状`ce-work`返回：当`behavior_change: true`时，它必须命名使用的回归测试、检查的现有测试、测试added/changed或未更改地使用、修复之前观察到的红色故障或特征、验证运行以及任何故意的测试异常。不要在 LFG 内部决定测试策略；证据就是`ce-debug`的合同。带有 `behavior_change: true` 的 `fixed` 返回，并且证据缺失或太模糊，无法说明修复是如何被证明的，从而停止运行并报告缺失的字段。此路线上没有恢复调用：`ce-debug`没有协调路径，第二次运行将重新调查。

## 仅发送用户提供的内容

用户要求进行此修复。他们没有提供分支和树已经承载的任何其他内容：修复未触及的未提交文件，或者在该分支的开放拉取请求中尚未接受审查的超出基础的提交。返回中的`pre_fix_scope`告诉您修复之前存在什么；它是唯一的记录，因为修复提交现在位于其之上。在此运行推送的任何步骤之前，包括审查修复提交，决定是否提供推送将发布的所有内容：修复、此运行本身添加的内容（包括 `pre_fix_scope.caller_edits`、编辑此运行为用户在调用 `ce-debug` 之前要求的工作所做的操作）以及开放的 PR 已保存的先前工作。如果是这样，请照常发布，并将脏文件排除在每次提交之外。如果不是，或者您无法判断，请保留：在本地提交修复，不让任何步骤发布，记录剩余的发现，读者无需使用 PR 即可找到它们，并说出被阻止的内容以及 `ce-debug` 在用户仍在处理的分支上直接调用的内联修复。

## 后续步骤会收到什么而不是计划路径

- **第3步，`ce-simplify-code`：**传递`changed_files`作为范围，而不是分支差异，因此传递无法到达用户未提供的工作；传递`root_cause`作为简化必须保留的结构，因此修复不会被简化掉；传递 `mode:pipeline`、`size-cutoff:` 令牌步骤 3 名称，以及每个测试 `verification_evidence` 名称作为其自己的 `proof-test:<path>` 来证明修复。
- **第 4 步，`ce-code-review`：** 没有 `plan:` 参数。它的需求检查是通过它自己的合同来补充的，并且它从提交中推断出意图；将 `root_cause` 摘要作为审核上下文传递。审查没有仅限修复的范围并读取工作树，因此它可能会报告用户未提供的文件；步骤 5 仅将结果应用于 `changed_files` 以及此运行自己的编辑，并将其余部分报告为残差。
- **步骤 6 和步骤 9：** 已解决的决策概要从未在此路线上编写，因此不会渲染已解决的决策出处线。将 `root_cause`、`issue_of_record` 和任何非空 `prevention_signal` 到 `ce-commit-push-pr` 作为 PR 描述上下文传递，因此 PR 主体携带诊断和建议的信号并链接或关闭票证，并命名必须保留在提交之外的文件。
- **步骤7，`ce-compound`：**同样的反事实适用；经过调试的根本原因是持久学习的最常见形式。
- **第11步，收尾：**下一份工作offer读取计划，未做出。将任何非空 `prevention_signal` 声明为本次运行未实现的提案。
