# 监视循环 — 调度、状态、重复数据删除、边缘情况

在对第一个刻度的输出进行操作之前，请在每个PR 看护会话中阅读一次此内容。它涵盖了如何在每个宿主上安排蜱虫，磁盘上的状态文件保存什么，保持蜱虫幂等和崩溃安全的声明→行动→确认协议，以及边缘情况。 SKILL.md 表示刻度顺序； `references/tick.md` 保存命令。

## 手表如何自我维持

继续监视直到满足停止条件。 **选择下面的唤醒源**决定是什么让该代理恢复；默认是变化检测器`pr-snapshot watch`。它按一定时间间隔运行快照的 fetch→diff，使用**无代理令牌**，并*仅*在有要检查的工作或停止条件时打印一行 `BABYSIT_WAKE {reason,url,...}` 行，然后退出。使用宿主工具等待该线，运行一圈，然后重新装备探测器。使用检测器作为唤醒源，在等待时保持会话处于活动状态，以便每次唤醒都会返回到该代理，并且对话的决策完好无损。

滴答声由新快照决定，而不是由唤醒原因决定。原因说明了探测器为何发射以及哪个引用拥有后续：

| 唤醒原因 | 探测器为何发射 | 拥有者 |
|---|---|---|
| `actionable` | 未解决的线程或对当前头的检查失败 | `references/tick.md` |
| `feedback-candidate` | 还是需要resolver判断的非线程反馈。解析器通过默默地丢弃它是正常的分类结果，而不是检测器误报。 | `references/tick.md` |
| `branch-currency` | 需要索赔、检查、决定或调节的货币项目 | `references/branch-currency.md` |
| `unrequested-base-merge` | 没有声称的货币项目产生的头部的基础合并 | `references/branch-currency.md` |
| `base-ref-blocked` | 当前基地身份尚未得到证明（请参阅下面的**当前基地合并身份**） | 这个文件 |
| `stack-blocked`, `blocked-failing`, `needs-human` | 常设残差 | `references/settle.md` |
| `downstack-actionable` | 重新开放较低的托管堆栈层 | `references/stack.md` |
| `blocked-external`, `blocked-external-drained` | CI正在等待维护者批准； `blocked-external-drained` 标志着审核流失的结束 | `references/settle.md` |
| `merge-ready` | PR 通过稳定窗口保持安静，并处于看起来就绪的门接受的合并状态 | `references/settle.md` |
| `review-evidence-moved` | 当加宽的稳定窗口运行时，准备就绪状态发生了变化。重新判断，而不是抱着已经发生变化的证据，睡在窗外。 | `references/settle.md` |
| `terminal`, `max-runtime` | PR关闭或合并，或者调用预算用完 | `references/settle.md` |
| `stop-signal` | 观察者被告知停下来；结束循环并报告 | 这个文件 |
| `invocation-superseded` | 稍后的显式调用拥有该状态 | 这个文件 |

在固定期限内，最终刷新保留 `terminal` 并停止已解决的 `merge-ready`。否则，`max-runtime` 的排名高于每个非终端工作或残余唤醒，因此上限无法启动另一轮代理。

观察者所有权是 **latest-valid-watcher-wins**：完成有效第一个快照的最新调用将接管。较新的调用会取消较旧的调用，而较旧的调用的第一次提取仍在进行中，因此网络完成订单无法将所有权交还给较旧的调用。该保留不会取代已经处于活动状态的观察者。只有成功的第一个快照才会取代活动观察者并优雅地终止它；失败的预检会让活跃的观察者保持健康。每个唤醒和快照都带有`watch_generation`。当唤醒到来时，将其生成与新快照进行比较。陈旧的唤醒将被丢弃并合并到当前读取中。如果生成匹配但注意集（快照表示仍需要操作的项目）已清除，则不执行任何操作。 `invocation-superseded` 唤醒意味着稍后的显式调用现在拥有该状态：结束旧循环，无需勾选或重新准备。替换观察者保留 `last_change_at`、`invocation_started_at` 和 `invocation_budget_seconds`，因此它会立即轮询，而无需添加新的结算延迟或更新预算。

使用宿主的工具运行检测器并等待其输出。技能驱动工具调用；它不会像用户那样输入斜杠命令。下面的行是示例，不是必需的工具列表：

| 马具 | 运行和等待工具 | 在会议结束后仍能持久吗？ |
|---------|--------------------|-----------------------------|
| Claude Code (CLI) | 背景`Bash` + `Monitor`/等待；或`/loop`下的`ScheduleWakeup` | 否（会话绑定）——cron 表示持久 |
| 格洛克 (CLI/TUI) | 背景`run_terminal_command` + `get_command_or_subagent_output`； `scheduler_create --durable` 用于跨会话安排 | 是，通过 `scheduler_create --durable`（60 秒分钟，7 天） |
| 光标 (CLI) | `Shell`背景+`notify_on_output`哨兵（其`/loop`是用户输入的，**不是**技能可调用的） | 否（会话绑定） |
| Codex (CLI) | `exec_command` 启动检测器，然后`write_stdin` 等待返回的进程会话 | 否（会话绑定） |

**用户可运行的恢复语法。** 每当此引用告诉技能打印或复制恢复调用时，默认为`/ce-babysit-pr <url>`，并且当运行姿势不是`target`时，附加相同的`posture:stack-ready`或`posture:stack-land`令牌，以便检查点/持久/会话重新进入保持堆栈范围。仅当活动主机为 Codex 或明确记录以美元为前缀的技能调用时，才使用 `$ce-babysit-pr <url> [posture:…]`。仅将调用呈现为内联代码并仅输出一种形式。

**检查点：** 仅当用户请求或没有任何东西可以唤醒此代理时才使用检查点模式。运行一次，保留状态，报告并打印准确的主机渲染的恢复调用。假设监控已暂停。切勿伪造带有前台 `sleep` 或非托管分离进程的循环。

**耐用性：** 会话中的手表会随着会话而消失。重新调用技能会从磁盘恢复，因为 `/tmp` 在各个刻度中持续存在。对于无人值守的多日监视，请升级为耐用的调度程序：Grok 的 `scheduler_create --durable`，或运行 `<cli> exec '<host-rendered resume invocation>'` 的 cron。新的无头运行没有此对话的记忆，因此将相应的决策保存到磁盘中。

## 选择唤醒源

每次滴答时，一个唤醒源都会将该代理带回来。在第一次等待之前，从您现在拥有的主机说明和工具中选择一次：

| 楼主所说的PR等待 | 唤醒源 |
|---|---|
| 它的指令决定了它们的工作方式，例如需要它自己的 PR-watch 工具，禁止轮询或后台观察者，或者告诉你在等待时结束回合 | 主机机制。不要运行检测器。 |
| 什么都没有，或者它只提供了一个可选的 PR-watch 工具 | 检测器可以看到比主机的事件源更多的状态。不要添加主机的工具。 |
| 它的指令或工具使该运行无法被唤醒，例如不得等待的委托运行 | 检查点，或在 `mode:pipeline` 一次勾选后返回。 |

此处，主机指令的优先级高于该技能的默认值。切勿运行两个源来满足这两个规则：这会打破单观察者边界并产生重复的唤醒。当武装唤醒源可以使该特工返回时，结束转弯是正确的，而当没有任何东西可以返回时，结束转弯是错误的。

唤醒源仅决定控制权如何返回。每个刻度仍然从新快照开始，并且仍然像往常一样运行 `ce-resolve-pr-feedback` 和 `ce-debug`。标记、姿势和真实止损不会改变。该报告仅添加了哪些 PR 活动可能会被忽视。

无论哪个唤醒源正在运行，主机事件都是查看的原因，而不是事实。任何事件，包括 PR 合并的事件，都只会提示一个新的快照和一个普通的勾号。快照的`pr_state`决定。在 `stack-land` 下，此运行自己的土地步骤保持图层过渡 (`references/stack.md`)。忽略运行报告后出现的任何唤醒。

当主机机制为唤醒源时：

- **在第一次等待之前运行完整的滴答。** 主机手表可能仅在启动后发生事件时唤醒，因此 PR 上已有的反馈和故障由您首先处理。遵循主机的布防合同：请勿重新布防唤醒后仍保持开启状态的手表。
- **结束回合之前再次快照。** 在滴答期间发生的事件可能永远不会产生唤醒。如果新快照显示任何可操作的内容，请运行另一个刻度而不是等待。
- **不要唤醒批量评论。** 评论合并窗口属于检测器。大量评论可能会花费额外的解析器通行证，而标记可以防止这些通行证重复工作。其新鲜快照显示任何可操作内容的唤醒不需要解析器或调试通道，但仍会判断停止条件：没有 `merge-ready` 唤醒会为您做这件事。
- **说出此源可能错过的内容。** 主机可能不会在每个反馈表面、落在其底座后面的分支上或时钟耗尽时唤醒。稍后的唤醒快照会拾取任何遗漏的内容，因此在唤醒持续出现时不会丢失任何内容。每当您报告 PR 状态时，请命名该主机的唤醒未明确涵盖的任何流。 `references/settle.md` 表示当只剩下定时等待时该怎么做。
- **检查每个刻度的预算。** 探测器不会触发 `max-runtime`。此模式计算挂钟时间，因此将 `invocation_elapsed_seconds` 与 `invocation_budget_seconds` 进行比较，并在达到预算时停止。
- **当运行停止监视此 PR 时释放它。** 在每次真正停止和每次托管堆栈层转换时释放主机的监视。监视已删除的主机（例如在合并时）并不是失败。

## 节奏（观看间隔）

- `pr-snapshot watch --interval` 是轮询节奏：PR 活动时约为 2-3 分钟，安静时加宽至约 5-10 分钟。检测器很便宜，但每次轮询都是 `gh` 调用。荣誉GitHub速率限制重置标头并在`403`/`429`上退出；声明→行动→确认使得在短暂的 API 错误后恢复是安全的。
- `--settle-seconds`（默认 300）是`merge-ready` 唤醒之前的安静窗口。让它在正常手臂上保持未设置状态；该脚本的默认值是初始策略。只有`references/settle.md`决定何时设置它。
- `--feedback-coalesce-seconds`（默认 180）是 **仅评论** 唤醒之前的安静窗口。让它在正常手臂上保持未设置状态。在第一条评论上醒来将花费完整的 `ce-resolve-pr-feedback` 调度来结束“状态噪音”，并将普通序列（推送 -> 机器人评论 -> CI 完成）分为两轮代理。在窗口运行时，候选项保持可操作状态，因此任何其他唤醒都会在其滴答声中处理它们；没有任何东西被丢弃，只是被推迟。
- `--blocked-external-drain-seconds` 仅在交互式批准门唤醒后设置（`blocked-external`：CI 正在等待人工批准）。在这段短暂的 300/900/1800-second 审查周期中保持活跃的约 150 秒间隔：安静的 5-10 分钟轮询可能会在任何信号到达之前消耗掉整个层。持久的头部范围审查时钟决定到期时间，而不是手臂时间，也不是更广泛的合并就绪安静时钟。
- 推动或其他突变会移动头部。以活动节奏重新启动 `watch`，以便读取新状态。
- 每次重新武装都呈现相同的`--invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS"`；助手拒绝更改的令牌、锚点或预算。只有第一个快照使用`--start-invocation`；只有托管堆栈层转换使用`--continue-invocation`。

## 管道模式绑定 (`mode:pipeline`)

协调器 (`lfg`) 内联驱动刻度并需要终止循环。连续运行，直到下面的停止点之一。 **要等待 CI 在刻度之间进行，请使用该工具的本机非阻塞等待 - 绝不是裸露的前景 `sleep`** （在 Claude Code 上阻塞，在其他地方不鼓励）。示例：Claude Code 的 `Monitor` 直到循环； Grok 的 `get_command_or_subagent_output(timeout_ms=…)` 或 `monitor`；光标的`Await`位于背景`gh pr checks --watch`上。当主机指示 PR 等待并且其唤醒返回到此会话时，启动唤醒并结束回合；唤醒会恢复这些滴答声。如果没有任何东西可以唤醒运行，请执行一次滴答操作并将控制权返回给协调器，而不是忙于旋转。循环直到：

- `references/pipeline.md`处的管道停止返回成功或`needs-human`；它拥有两个大门。任何缺少它们的东西都会继续滴答作响，直到它被清除或时间预算到期；或者
- 达到了**预算**。默认为每个头谱系 **3 CI 修复回合**，总时间上限约为 30-45 分钟。当预算用完时，仍然是红色的支票和任何 `needs-human` 项目都会成为剩余。

切勿在管道模式下等待合并就绪结算窗口或人工审核；这些是互动站点。超过时间上限的检查卡在 `IN_PROGRESS` 上，以“CI 仍在运行”残差结束运行，而不是永远阻塞。

round/time 预算是一个粗略的成本限制，可以防止失控。宁愿停下来*因为工作显然没有收敛*。下一节将介绍如何决定。

## 不收敛（触发→路线→停车→重新开放）

循环可能会在未完成的情况下搅动。三种形状：CI **乒乓球**（修复A表面B，修复B使A恢复，通常是一个紧急的权衡）；审查机器人**跑步机**（每次提交都会产生新的尼特）；和 **错误方法打地鼠**（每个 nit 都是有效的，但方法，比如正则表达式，是问题所在）。原始尝试计数器无法将这些与“合法进度”区分开来（四个独立的失败，每个失败一次）。所以决策是代理对轨迹进行推理，并且职责划分是严格的：

- **`pr-snapshot`（PR 看护）报告事实。** `trajectory` 块是确定性且粗糙的。 `check_recur_max`/`recurring_checks` 计算失败、清除、然后在*新*头上再次失败的检查；排除了同头拍动，因此这不是片状噪声。 `unresolved_trend` + `new_threads_this_tick` 显示积压不断增加，新线程到达。 `stream_alternations` 统计 ci↔ 评论跳出，这是只有PR 看护才能看到的跨流流失。 `heads_since_progress` 计算未解决问题中未创出新低的头数。 `invariant_rounds` 计算每个唯一头的解析器提供的 `invariant_key` 值；该脚本永远不会从路径、正则表达式或注释文本中推断出键。 Babysit **从不**给任何这种“不融合”贴上标签。
- **叶子评委。** 叶子是该蜱的委托技能：`ce-debug`用于CI，`ce-resolve-pr-feedback`用于审查。当跨越触发器时（阈值仅存在于 `references/tick.md` 中），在修复、提交或推送之前，将轨迹作为 **强制输入** 传递到该蜱虫的叶子。然后叶子会做两件事之一。它通过命名其下一个有界修复解析的不变量来展示进展。或者它返回一个`needs-human`，**停放整个流**（将其作为常备残差搁置）和`decision_context`：张力或根本原因、选项、它们的权衡及其精益。
- **不变键。** 在 **fix** 结果中，叶子为它修复的每个根返回一个稳定的`invariant_key`，与根覆盖的项目相关联。叶子不运行`pr-snapshot`并且不标记。 Babysit 将每个键保留在其现有的已调度标记上（`--thread` / `--comment` 加 `--invariant-key`）。不相关的密钥保持独立可操作，并且密钥上的一轮或两轮进展不会成为障碍。

**防狼叫线（放到叶子上）：** *渐进式故障迁移*（A固定，B出现一次，B固定，完成）为普通修复； **请勿停车。** *振荡*不收敛；公园。振荡看起来像以下任何一种： A 在 B 修复后返回；失败的设定周期；缺陷迁移X→Y→Z，且不满足相同的不变量；或固定大小超线性增长。 “我们已经尝试了很多”是远远不够的。

**计数器不能错过的第三种情况：在兄弟站点之间重复出现的“正确”发现。**有时，每个新头都会带来一个“有效”的新线程，并与已经固定的线程共享一个根和一个处理。这不是错误接近的集群，也不是振荡。这是一种具有多地点爆炸半径的修复方法，每个头可处理一个地点。为每个人修复一个站点就像错误地停车一样浪费。 **路由它，不要在这里决定它：**传递循环反馈集群**加上**到`ce-resolve-pr-feedback`的轨迹并请求**有界类评估**。解析器具有差异并进行调用。它决定站点是否真正等效（相同的不变量，相同的修复，仅涉及此PR的行为），枚举具体位置，并一次性修复类。 Babysit **不**从 `trajectory` 推断根或站点；这些是流失计数，而不是语义同一性。如果解析器判断站点*不*等效，则会回退到每个站点修复。如果它判断共享根的方法是错误的，它就会停止，如上所述。

**守卫：**

- **移动目标≠不收敛。** 基础分支合并、依赖关系碰撞、不稳定的基础设施和机器人规则更改会产生不相关的新故障。复发已经排除了相同 SHA 的抖动。尽管如此，不要将叶子归因于外部原因而不是方法的故障。
- **跨流矛盾。** 如果 `ce-debug` 认为审核请求的行为无效，而 `ce-resolve-pr-feedback` 认为审核请求的行为是必需的，则为单个 **跨流** 残差。切勿随意将车停在一侧。
- **停放的流仅在下面的决策生命周期内重新打开。**没有流有自己的重新打开规则。

## 磁盘状态合约

状态位于`<scratch-root>/ce-babysit-pr/<host>-<owner>-<repo>-<pr>/state.json`。该路径是稳定的并且可以在调用之间重用，因此任何后续的标记（计划的或手动运行）都可以找到它。 GitHub Enterprise 需要 `<host>` 段（来自 PR URL；`github.com` 在公共主机上）：如果没有它，在不同主机上共享 `owner/repo#N` 的两个 PRs 将重复使用一个 `state.json` 并进行交叉污染处置。 `pr-snapshot` 脚本在文件锁定下执行所有读取和写入。形状：

```json
{
  "pr": { "owner": "...", "repo": "...", "number": 123, "url": "..." },
  "head_sha": "abc123",
  "tick": 7,
  "state_created_at": "<iso8601>",
  "started_at": "<iso8601>",
  "invocation_id": "<opaque invocation token>",
  "invocation_budget_seconds": 28800,
  "last_activity_at": "<iso8601 — activity heartbeat: last watch poll or agent snapshot/mark>",
  "dead_time_seconds": 0,
  "invocation_backstop_seconds": 259200,
  "watch_generation": "<opaque generation>",
  "watch_pid": 12345,
  "watch_process_identity": "<pid-reuse guard>",
  "checks": { "<check_key>": { "name": "...", "status": "COMPLETED", "conclusion": "FAILURE", "head_sha": "abc123" } },
  "threads": { "<thread_id>": { "last_comment_id": "...", "last_comment_at": "<iso8601>", "disposition": "open|dispatched", "acted_identity": ["<comment_id>", "<comment_at>"] } },
  "feedback": { "<comment_or_review_id>": { "kind": "comment|review", "author": "...", "disposition": "open|dispatched", "acted_identity": ["<edit_id>"] } },
  "ci_dispatched": { "<head_sha>": ["<check_key>", "..."] },
  "human_decisions": [{ "id": "decision:<hash>", "residual": "<complete typed residual>", "sources": [{ "kind": "check", "id": "CI/test", "observation": "<frozen source facts>" }] }],
  "answered_human_decisions": [{ "id": "decision:<hash>", "answer": "<exact human response>", "residual": "<complete typed residual>", "sources": ["<same frozen observations>"] }],
  "review_decision": "APPROVED",
  "blocked_external_head_sha": "abc123",
  "blocked_external_first_seen_at": "<iso8601>",
  "blocked_external_review_last_activity_at": "<iso8601>",
  "mergeable": "MERGEABLE",
  "merge_state_status": "CLEAN",
  "base": {
    "host": "github.com",
    "repository": "owner/repo",
    "ref": "main",
    "oid": "live-base-sha",
    "graphql_oid": "graphql-live-base-sha",
    "historical_oid": "historical-pr-base-sha",
    "merge_commit_oid": "generated-test-merge-sha",
    "merge_parent_oids": ["live-base-sha", "head-sha"],
    "identity": "current"
  },
  "base_ref_blocker": null,
  "branch_currency_state": {
    "current_key": "currency:<identity-hash>",
    "head_sha": "abc123",
    "items": { "<currency-key>": { "status": "BEHIND|DIRTY", "disposition": "open|claimed|confirmed", "host_branch_update_capability": true, "recovery_state": "claimed|mutation-observed|ambiguous|retry-authorized|retry-exhausted", "semantic_conflict_fingerprint": "<paths-and-stage-blobs>" } },
    "semantic_parks": { "<fingerprint>": { "head_sha": "abc123", "status": "DIRTY", "route": "normal-base", "observation_key": "<currency-key>" } }
  },
  "pr_chain": {
    "manager_status": "confirmed|absent|probe-error",
    "manager_source": "gh-stack|graphql|null",
    "relationship_status": "dependent|independent|probe-error",
    "target_position": 2,
    "target_needs_rebase": false,
    "upstack_needs_rebase": [],
    "entries": [],
    "parent_prs": [],
    "dependent_prs": []
  },
  "last_change_at": "<iso8601>",
  "last_action": "<short string>",
  "trajectory": {
    "check_history": { "<check_key>": { "state": "failing|clear", "last_head": "abc123", "recur": 0 } },
    "seen_threads": { "<thread_id>": 3 },
    "unresolved_series": [2, 3, 4],
    "stream_series": ["ci", "review", "ci"],
    "min_open_problems": 1,
    "heads_since_progress": 0,
    "invariant_heads": {}
  }
}
```

`human_decisions` 是跨审查、CI 和分支货币的唯一持久决策集。当前的决定是一个硬性阻碍：PR在其存在时*不*准备好合并。它涵盖了冻结在其 `sources` 中的精确观察结果；源记录仅保留普通的open/dispatched/claimed事实。快照在 `needs_human_residuals` 中发出每个未更改的负载，并将其与 `human_decisions` 视图中的 `decision_id` 配对，用于渲染和路由答案。任何所涵盖的观察结果发生变化或消失都会使整个决定无效，并使幸存的普通来源再次变得可行；远程活动永远不会被推断为答案。 `mark --answer-decision <decision_id> --answer-file <path>` 是唯一的答案转换。它将精确记录移动到`answered_human_decisions`，保留响应，同时匹配源仍然可操作，并防止未更改的证据立即重新停车。当智能体单独证明观察不再是问题时，显式来源`--disposition open`可能会取消覆盖决策。切勿自动拒绝、自动解决或默默等待决定。没有完整有效负载的旧式停放记录无法打开：它们不会阻塞，并且它们的源返回到普通的可操作工作。

`check_key` 是 `"<workflow>/<name>"`（如果没有工作流程，则为 `"<name>"`）。对于同一头，它在各个轮询中都是稳定的，这就是重复数据删除的全部需求。两个快照字段很容易被误读。 `persisted_state_age_seconds`是可恢复的PR日志存在的时间；它永远不会计入 `invocation_elapsed_seconds` 衡量的调用预算。当审核开始或在批准门等待期间发生更改时，`blocked_external_review_moved_this_tick` 为 true。即使门本身在布防时已经存在，它也会唤醒代理，因此代理可以选择更长的排水管。 `references/settle.md` 拥有排水时钟。

## 声明 → 行动 → 确认（重复数据删除协议）

这是使刻度幂等*和*崩溃安全的规则：**快照永远不会标记仅通过观察来处理的项目。**仅当代理确认其已执行操作（通过`mark`）或远程真理将其删除时，项目才会离开可操作集。因此，如果解析或调试过程崩溃、错误或未完成就返回，则该项目在下一个周期仍然可操作。循环不能默默地放弃工作。

- **查看线程。** 线程在未解决并且您尚未记录对其执行操作时是可操作的。在解析过程之后，`mark --thread <id> --disposition dispatched`处理普通的未解析线程；当叶子返回`invariant_key`时，相同的标记携带`--invariant-key`。共享残留标记冻结其完整的源观察结果，而不改变它们的配置。后来的审稿人评论使任何覆盖决定无效，并重新开放每个幸存的兄弟姐妹；它不回答该决定。每个标记都带有活动的调用元组（调用 ID、开始锚点、预算），因此过时的标记无法使新调用中的工作停止。
- **非线程反馈候选人**（顶级PR评论+评论提交机构）。这些没有远程解析操作，因此传递给解析器的每个候选者必须被标记为 `dispatched` 或被一个经过验证的当前决策覆盖。被派遣的候选人在正文编辑过程中保持沉默，因为状态机器人会定期重写他们的评论；对涵盖的候选人进行编辑会使决定无效。新评论具有新 ID 并且可操作。两个反馈界面都算作轨迹和待办事项核算的一个审核流。
- **CI 检查。** 当前磁头的失败检查是可操作的，直到您`mark --check <key>`。类型化决策通过共享剩余标记进入相同的规范集，而不是通过特定于检查的决策状态。新头清除调度状态，使检查来源的残差无效，并根据新提交重新评估决策。
- **当前基合并标识。** GitHub 的可合并判决仅在根据现在的基进行计算时才可用。 `base.historical_oid`是PR的历史`baseRefOid`；它可能会在基础分支前进之后合理地滞后，并且永远不会自行阻塞。 `base.graphql_oid`是`baseRef.target.oid`，`base.oid`来自对基本参考的独立精确读取。仅当这两个实时碱基读取匹配并且`potentialMergeCommit`将该碱基和观察到的头命名为其两个父级时，可合并结果才是当前的（`base.identity == "current"`）。否则，身份是一个阻碍：`race`当碱基在读取之间移动时，`mergeability-pending`当GitHub尚未生成测试合并时，`probe-error`当读取失败或格式错误时。拦截器禁用`mergeability_certain`，不发出任何分支货币项目，并唤醒`base-ref-blocked`；准备等待证明绑定的新观察。一种 `race` 本身并不清楚：当唯一不匹配的是测试合并的基础父级（头和实时基础一致）时，GitHub 可以无限期地将测试合并保留在旧基础上。它立即算作`stale-computation`，不再阻塞； `merge_computation_stale` 进行了披露。 `DIRTY` / `CONFLICTING` 是后备：GitHub 可能会省略 `potentialMergeCommit`，因此匹配实时库读取使冲突结果无需生成合并即可使用。
- **分支货币。** `branch_currency` 是第三个注意力流。它的身份绑定了主机限定的实时基repository/ref/OID、头部 SHA、合并状态和路由。 “可针对当前基数合并”和“头部包含最新基数”是单独的问题；带有GitHub报告`CLEAN`的普通历史基地移动不需要维护。具有开放子女家属的根仍然有资格获得自己的项目。已声明的项目仅保持协调状态，直到其被确认或移交给共享决策步骤，并且声明或决策永远不会转移到移动的头部或底座。没有安全自主延续的终端货币结果成为残差，其来源为`{ id: <currency_key>, kind: "currency" }`；它使用上面的共享答案转换，并且没有单独的答案状态。哪些状态会发出物品、索赔生命周期以及 `BEHIND`/`DIRTY` 维修都在 `references/branch-currency.md` 中。

`human_decisions`、`answered_human_decisions`、`ci_dispatched`，线程和反馈配置，`branch_currency_state` 共享锁定状态日志。没有第二个决策分类账，也没有特定于路线的崩溃恢复记录。

## 合并准备和结算窗口

不要重新推导“必需的检查”或必需的审查； GitHub 已经计算它们了。 `references/settle.md` 拥有看起来准备好的大门。引擎事实如下：

- `UNSTABLE`表示可合并，但非必选的勾为红色； `BLOCKED` 表示未满足所需的门。即使 `merge_state_status` 是 `UNSTABLE`，`has_failing_checks` 也可以让您对红色支票进行操作。
- 每当就绪状态发生变化时，脚本都会标记 `last_change_at`：检查状态或结论、线程的身份（添加、编辑或解析）、头 SHA、`review_decision`、明确的 `mergeable` 或 `merge_state_status`，或当前基础身份。基端移动和 GitHub 重新计算不会对其进行标记，因此繁忙的基端分支无法阻挡安静的窗口。自该标记以来，每个快照都会发出 `quiet_seconds`，因此仍在工作的审查者或机器人会显示为最近的活动。
- 安静是冷静的信号，而不是保证。是否仍会进行审查是代理对解决决定的判断，而不是引擎跟踪的状态。

## 并发性

- **锁定。** 该脚本在每个读取和写入状态周围获取文件锁定。锁无法覆盖代理自身的突变，这种突变发生在脚本调用之间，因此它是必要的，但还不够。将快照视为提示，而不是作为世界在突变时不变的保证。货币突变首先重新验证其声称的观察结果（`references/branch-currency.md`）。

## 托管堆栈延续

`references/stack.md` 拥有姿态、层转换、上栈维护和着陆。它依赖的监视机制：一个活动的 PR 目标和一个监视程序，每个堆栈层从来没有一个监视程序。当主机的手表是唤醒源时，在每次转换时将其移动到新层并报告较低层未被监视，除非一个主机手表也可以覆盖它们。使用 `--continue-invocation` 和以下值初始化每个新层的状态目录：

- `--invocation-id`、`--session-started-at`（锚标记，而不是`--invocation-started-at`）和`--invocation-budget-seconds`，具有与第一个快照使用的相同记录值。
- `--continue-dead-time-seconds <prior layer's invocation_dead_time_seconds>`.
- 在继续调用时，重新声明相同的 `posture:` 标记。

 每层的状态目录都会累积自己的死区时间，因此省略进位值会将前一层的挂起时间重新计为活动时间。一个固定预算涵盖整个接受的遍历，而不是每PR重新启动。从本次运行的 `stack-land` 着陆步骤中刚刚着陆的 MERGED 是层转换，而不是运行的终端出口。

## 边缘情况

- **托管堆栈：** 单独的主干移动并不是重新堆栈的理由。管理器的 `needsRebase` 标志打开以进行普通主干漂移，并且 GitHub 已经将其计入目标与其父基础的可合并性中，因此 `stack_blocker` 为空，并且只要 GitHub 报告某个 `MERGEABLE`/`CLEAN` ，目标就可能准备就绪。仅当目标陈旧或新鲜度未知时，`stack_blocker` 才是 `target-needs-rebase` / `managed-freshness-unknown` **并且** GitHub 不会清除它；就变成了`stack-blocked`。切勿在托管目标上使用 `gh pr update-branch` 或本地基础合并。推前基线和推后上栈维护位于`references/stack.md`。
- **手动依赖链：** 将请求的 PR 作为目标，限定相对于其父级的准备情况，并报告下游影响。符合条件的发出的 `normal-base` 项目仍可以在目标本地进行修复 (`references/branch-currency.md`)，但绝不能变基、重写、重新堆叠或以其他方式改变其依赖分支。目标推动可能会使开放的孩子变得陈旧；这只是一个残差。
- **外部磁头更换/强制推动：** 磁头 SHA 在环路下方移动。快照自动清除SHA范围的CI状态；只是重新快照。永远不要破坏不相关的推送工作。
- **PR 外部关闭或合并：** 在任何刻度上检测为 `pr_state != "OPEN"`，这是具有最终状态的干净退出。例外情况是来自此运行的授权 `stack-land` 着陆步骤的刚刚着陆的 MERGED，这是层转换（请参阅上面的托管堆栈延续），而不是终端退出。
- **无推送访问/分叉PR：**委托推送将失败。从委派技能的结果中检测到这一点，报告它，然后停止。循环无法取得进展，因为它没有取得进展的权限。
- **CI 永远不会完成：** 一个检查卡住 `IN_PROGRESS` 使循环无法稳定，直到调用预算结束它（`references/settle.md`，预算耗尽）。交回测得的 `invocation_elapsed_seconds` 和所达到的 `max_runtime_ceiling`，以便用户可以区分活动预算和 3 天的预算。

## 维持手表（第 5 步，全文）

**自维持手表在设置范围后自主运行。**它从不请求修复、推送、回复、解析和 PR-描述刷新的许可，并且堆栈范围的姿势不会在每一层重新请求。在交互式连续模式下，在既没有到达结束监视的停止点也没有到达托管堆栈转换的刻度后重新准备；当手表继续在其周围时，站立的残留物保持可见并阻碍准备或前进。在`mode:pipeline`中，改为应用上面的有界止损：当规范决策集非空并且没有剩余自主工作时，立即返回而不是重新武装。

使用检测器作为唤醒源，在移动头部的任何突变之后重新启动 `watch`，使用相同的调用 ID、开始和预算。未就绪但未阻塞的状态既不是停止也不是问题；继续等待唤醒源。观察者沉默不携带PR状态信息；这仅意味着没有触发唤醒条件。切勿从沉默中推断审核状态。当用户在唤醒前询问状态时，使用相同的调用字段运行新的 `snapshot` 并报告该状态。该循环唯一的交互式问题是步骤 1 的一次性状态和范围选择，当确认托管堆栈时，会在 `target` 下询问一次。

在 **检查点模式** 中，您在第 4 步之后就完成了；下一个刻度是用户重新运行该技能。因为每个时钟周期都可以从磁盘恢复，所以每次唤醒（`watch`哨兵、调度程序触发或手动重新运行）都是干净地重新进入步骤 2。
