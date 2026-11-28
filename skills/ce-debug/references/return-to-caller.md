# ce-debug — 返回调用者模式（非交互式，调用者拥有修复后的步骤）

当 `ce-debug` 被协调器（例如 `lfg`）在其缺陷路由上与 `mode:return-to-caller` 一起调用时加载。调用者要求修复错误并拥有修复后的所有内容：简化、审查、复合、进一步提交任何内容、推送、PR和CI。该技能对功能分支进行调查、修复、验证、提交，并返回结构化结果。它从不催促，也从不要求。

这不是`mode:pipeline`。管道模式在它已经拥有的PR分支上为PR 看护提供服务：它播种失败的作业，推送自己的提交，并跳过审查，因为PR 看护范围审查。这里没有任何内容被推送，并且调用者会进行评论。

## 什么保持不变

阶段 0 到 3 按照主体定义运行，调查严格性不变：因果链门、复制、升级表、`references/fix.md` 中的测试优先修复序列以及记录问题规则。第 3 阶段中的 **分支** 规则完全适用：在默认分支、独立分支或不确定分支上，在第一次编辑之前创建一个以 bug 命名的功能分支，并说明您移至哪个分支。在 `main` 上调用的 `/lfg fix this bug` 不得提交给 `main`。保留前缀范围记录和修复拥有的文件列表，因为返回是根据它们构建的：调用者仅发送用户提供的内容，并且此返回是它可以了解修复之前树或分支上已有内容的唯一位置。

## 有什么变化

- **阶段 0：** 如果问题获取失败，请继续使用您拥有的输入并在返回中记录差距。切勿要求用户粘贴内容。
- **第二阶段门：**不存在修复选择问题。调用者的调用授权了修复，因此仅使用 **收敛** 修复继续进入第 3 阶段。 **发散**修复，即会逆转故意的合同、行为或产品决策的修复，包括断言预期行为的“失败”测试，被推迟为 `needs-human` 和 `decision_context`，从未应用。当第 1 阶段的跟踪器和 PR 历史搜索发现针对同一错误的开放 PR 或其他正在运行的修复时，在您正在修复的分支以外的分支上，不应用任何内容并返回 `diagnosed-no-fix` 及其在 `summary` 中的链接；第二次修复只会重复它。切勿路由至 `ce-brainstorm`；设计问题是 `needs-human` 残差。当复制无法在这种环境下运行时，继续使用所能达到的最佳证据；如果因果链仍然有间隙，则返回 `needs-human` ，指出繁殖需要什么以及尝试了什么。
- **阶段 3：** 在功能分支上应用修复，将其验证为 `references/fix.md` 定义（红色然后绿色，可以在此处运行测试；否则文件允许的复制检查或特征记录在证据中），并仅提交修复拥有的文件。遵循上下文中已有的项目提交消息约定；否则遵循最近的日志模式，然后常规提交（对于此错误为`fix: <summary>`）。用户覆盖获胜。不要推。修复必须触及的文件已经包含用户未提交的编辑，在第一次编辑之前停止运行：返回`blocked`命名文件，不应用任何内容，因为没有提交可以将他们的编辑与修复分开，并且调用者无法为用户应答。这适用于所报道的网站；此类文件中存在相同错误的另一个站点将被保留并作为残留物返回，如 `references/fix.md` 所说。呼叫者关于用户提供了这些编辑的声明不会改变这一点。在调用此技能之前，调用者为用户要求的工作所做的编辑不是用户的。当它们位于修复拥有的文件中时，提交包含修复的文件并将其列在 `pre_fix_scope.caller_edits` 中；调用者对其他文件的编辑在 `dirty_files` 中保持不变。前缀范围记录在第 3 阶段编辑任何内容之前就已经知道了这一点。
- **阶段 4：** 跳过调试摘要块、修复后完善和审查步骤 (`references/post-fix-handoff.md`)、commit/PR 路由和学习捕获提供。发出下面的结构化回报作为该技能写入的最后内容。返回结束该技能，而不是回合。调用者在同一个会话中运行，返回后执行下一步。

## 结构性回报

返回结果是机器可读的；调用者解析它并根据精确的 `status` 拼写进行分支，因此永远不要重命名、缩写或添加它们。

```json
{
  "status": "fixed | diagnosed-no-fix | needs-human | blocked",
  "summary": "<一行：发生了什么>",
  "root_cause": "<the causal chain, trigger to symptom, with file:line references>",
  "changed_files": ["<修复拥有的文件，包括测试>"],
  "head_sha": "<修复提交后的 sha>",
  "branch": "<修复后提交修复的分支>",
  "prevention_signal": "<建议的日志字段、指标或断言，或 null>",
  "pre_fix_scope": {
    "head": "<修复提交之前HEAD>",
    "dirty_files": ["<files already modified or untracked before Phase 3 that are not fix-owned; left untouched>"],
    "caller_edits": ["<已包含调用会话自己的未提交编辑的修复拥有的文件，随修复一起提交>"],
    "commits_beyond_base": ["<commits the branch carried beyond the default branch before the fix, oldest first; empty on a fresh branch>"],
    "started_on_default_branch": false
  },
  "behavior_change": true,
  "verification_evidence": {
    "regression_test": "<文件和箱子，加上一条线，说明这条接缝捕获和遗漏的内容>",
    "existing_tests_inspected": ["..."],
    "tests_added_or_changed": ["..."],
    "red_before_fix": "<修复之前观察到的故障，或不可能进行红色运行时的表征>",
    "verification_run": "<commands and results>",
    "exception_reason": null
  },
  "residuals": [ { "type": "needs-human", "sources": [ ... ], "decision_context": { ... }, "thread_urls": [] } ],
  "issue_of_record": { "id": "<identifier>", "url": "<url>" },
  "blockers": [],
  "standalone_shipping_skipped": true
}
```

- `fixed`：应用收敛修复，其回归测试先红后绿，并且修复拥有的文件被提交到功能分支上。没有什么被推动。
- `diagnosed-no-fix`：根本原因已确定，但本次运行未应用任何修复，因为不存在安全收敛修复或其他地方已存在安全修复；当一个人必须决定某件事时，`residuals`带有原因，否则`summary`则带有原因。
- `needs-human`：解决方案将是发散的，或者如果没有只有一个人可以做出的决定，因果链就无法闭合；没有应用任何内容； `residuals` 在相同类型的剩余合约`references/pipeline-mode.md` 定义中携带`decision_context`。
- `blocked`：所需的读取失败，修复拥有的文件携带用户的编辑，或者无法准备工作空间； `blockers` 命名它，但没有提交任何内容。

`pre_fix_scope` 出现在每次返回中，并记录修复之前分支和树所携带的内容，如观察到的事实：前缀 `HEAD`、已经脏且不属于修复拥有的文件（修复从未触及它们）、包含调用会话自己的编辑的修复拥有的文件，以及超出默认分支的提交（推送或未推送）。它不对用户提供的内容做出任何判断；调用者决定这一点，而这条记录就是它做出决定的依据。当输入不带票据时，`issue_of_record`是`null`。每次 `fixed` 返回时都会出现 `verification_evidence`；当`behavior_change`是`false`（纯粹的测试或工具修复）时，`exception_reason`说明为什么不可能出现先红后绿的情况。每次退货时都会出现`prevention_signal`。它携带 SKILL.md 的第 2 阶段发现块描述的始终开启信号建议，因为此模式会跳过本来会显示它的切换，并且当该块的条件不成立时，它是 `null`。这是一个提案，而不是残余，并且不会添加到修复中。当没有时，`residuals`是一个空数组。不要发明残差类型；非阻塞后续操作在 `summary` 中进行。
