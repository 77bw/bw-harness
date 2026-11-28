# 勾选：快照、观看、标记、排序

在第一个快照之前阅读此内容。

## 第 2 步：运行 1 个刻度

蜱虫完全可以从磁盘恢复，因此任何重新调用都会驱动它：调度程序、`/loop`，或者用户一小时后重新运行该技能。将 `SKILL_DIR` 设置为包含此 SKILL.md 的目录，然后批量快照两个流：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && chmod 700 "$SCRATCH_ROOT" || { echo "unsafe scratch root: $SCRATCH_ROOT" >&2; exit 1; };
STATE_DIR="$SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>";
(umask 077; mkdir -p "$STATE_DIR") || exit 1; chmod 700 "$STATE_DIR" || exit 1;
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pr-snapshot" snapshot --pr <N> --repo <[host/]owner/repo> --state-dir "$STATE_DIR" --start-invocation --invocation-budget-seconds <seconds>
```

这是唯一可以启动预算的命令。传递用户请求的持续时间，或 **8 小时默认** (`28800`)。将输出的`invocation_id`、`invocation_started_at`和`invocation_budget_seconds`记录为`RUN_INVOCATION_ID`、`RUN_STARTED_AT`和`RUN_BUDGET_SECONDS`。需要`invocation_elapsed_seconds <= 60`；否则在武装观察者之前会失败。以后的每个快照、表臂和标记都必须呈现所有三个记录值；助手拒绝丢失或不匹配的令牌、锚点或预算。每个`snapshot`和`watch`，包括第一个，每当`references/branch-currency.md`为合并者留下`BEHIND`分支时，也携带`--defer-behind-to-merge`。在第一个快照之后切勿使用`--start-invocation`：重新准备、突变、重试、review/CI轮次和托管堆栈层转换（添加`--continue-invocation`）共享一个非滚动预算。持久的PR处置、重复数据删除和轨迹可以延续到新的调用；它的预算时钟却没有。

预算用于**活跃观看时间**，而不是原始挂钟时间。当会话中的手表运行时，整个过程暂停的时间段（关闭的笔记本电脑）将计入死区时间并从 `invocation_elapsed_seconds` 中排除。检测是粗略的：只有远高于轮询间隔的活动间隙才算作死时间，而普通轮询、代理滴答声和人为阻塞的等待则继续计数。重新准备会保留累积的死区时间，而不是重置它。单独的 **3 个日历日挂钟逆止器** 限制每次调用，无论死区时间如何；这是陈旧的 PR 或僵尸手表的上限。检查点模式、durable/cron路径和主机唤醒的手表没有连续轮询，因此它们计算挂钟时间。

将每个新鲜的`snapshot`视为评论线程状态的规范事实来源；它的捆绑获取对整个线程连接进行分页。切勿用一次性 `reviewThreads(first:N)` 结果替换它。如果确实需要直接诊断查询，请在得出计数或未解决状态结论之前遵循`pageInfo`直到`hasNextPage == false`。

**在自维持手表中，使用后台更改检测器返回刻度，除非主机的机制是唤醒源（`references/watch-loop.md`，选择唤醒源）。** `pr-snapshot watch` 在**无代理令牌**的间隔内运行相同的 fetch→diff，并*仅*在有要检查的工作或 stop/residual 条件时打印单个 `BABYSIT_WAKE {reason,url,...}` 行，然后退出。唤醒原因、每个引用所属的引用以及如何处理过时或被取代的唤醒都在 `references/watch-loop.md` 中。在使用宿主工具等待该线路时保持会话处于活动状态（步骤 1）；武装它：

```bash
SKILL_DIR="<absolute path of this skill's directory>"; SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && chmod 700 "$SCRATCH_ROOT" || { echo "unsafe scratch root: $SCRATCH_ROOT" >&2; exit 1; }; STATE_DIR="$SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>"; (umask 077; mkdir -p "$STATE_DIR") || exit 1; chmod 700 "$STATE_DIR" || exit 1; RUN_INVOCATION_ID="<invocation_id>"; RUN_STARTED_AT="<invocation_started_at>"; RUN_BUDGET_SECONDS="<invocation_budget_seconds>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pr-snapshot" watch --pr <N> --repo <[host/]owner/repo> --state-dir "$STATE_DIR" --interval 150 --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS"
```

在`stack-ready`/`stack-land`下确认的托管堆栈中，为该臂的每个打开的较低层附加`--downstack-pr <N>`，以便观察者探测下面的（`references/stack.md`）。

**不要**在普通手臂上传递 `--settle-seconds` 或 `--blocked-external-drain-seconds`。该脚本的 300 秒默认值是初始合并就绪结算窗口。只有步骤 3 (`references/settle.md`) 决定何时设置`--settle-seconds`。它在 `blocked-external`（批准门）唤醒开始有界审查耗尽后设置 `--blocked-external-drain-seconds`。

**Shell 状态在单独的工具调用之间不会持续存在。** `SKILL_DIR` 和 `STATE_DIR` 仅针对它们出现的命令进行设置。后面的 `mark` 调用（步骤 3 和 5）作为它们自己的调用运行，因此在每个命令中重新设置内联，或直接传递绝对路径。新调用中的裸`$SKILL_DIR`是空的，并且解析为错误的路径。

**GitHub Enterprise 需要`STATE_DIR` 中的`<host>`。** 从PR URL 的主机（或`gh repo view --json url`）派生；在普通的 github.com 上它是`github.com`。在每个`mark`中使用相同的值，因此在不同主机上共享`owner/repo#N`的PRs永远不会共享一个`state.json`。 **在 `--repo <host>/<owner>/<repo>`**（记录的 `[HOST/]OWNER/REPO` 选择器）中传递相同的主机：`pr-snapshot` 的第一个 `gh pr view` 在解析 URL 主机之前运行，如果没有选择器，它会查询结账的默认 `github.com`。

快照发出**注意集**：仍需要采取行动的项目。它包含您尚未采取行动的未解决的线程，**非线程反馈候选**（顶级PR评论+审查提交机构）您尚未分类，对您尚未分派的当前头进行失败检查，以及确切的当前`branch_currency`项目及其`attention`路线。 `counts` 总计线程、检查和评论；货币项仅出现在`branch_currency`中，因此零计数并不意味着注意力集为空。其余快照报告合并、检查、货币、时间、决策、`pr_chain`和`trajectory`事实；作用于字段的引用说明了它的含义。

是否根据当前基数计算`mergeable`由`base.identity`和`mergeability_certain`决定； `race`、`mergeability-pending`或`probe-error`身份禁用`mergeability_certain`并重新轮询（`references/watch-loop.md`，**当前基础合并身份**）。调用时间和持久化状态年龄是分开的；切勿将其中一个报告为另一个。 `pr_chain`带有两个独立的轴，`manager_status`（`confirmed|absent|probe-error`）和`relationship_status`（`dependent|independent|probe-error`），加上管理器源，target/upstack新鲜度，有序条目，以及普通的parent/dependentPRs（如果可用）。

`actionable.comments` 的成员是等待语义分类的候选者，而不是经过检测器验证的操作项。确定性提取仅排除空主体。来自PR作者的非空评论会保留下来，因为作者要求对其代理开放的PR进行更改是普通反馈； `dispatched` 标记（而不是作者身份）可以防止循环。提取不会根据内容、机器人身份或评论与评论表面来决定外部消息是否是有效反馈； `ce-resolve-pr-feedback`做出这样的判断。项目会保留在注意力集中，直到您确认对它进行了操作或分类 (`mark`) 或远程真理将其删除（已解析的线程从提取中删除），因此崩溃、失败或被取代的解析传递会将其项目留给下一个刻度。每个 `mark` 都呈现相同的 `RUN_INVOCATION_ID`、`RUN_STARTED_AT` 和 `RUN_BUDGET_SECONDS`，因此过时的解析器在它可以静默替换调用中的工作之前会失败。状态模式和声明→行动→确认协议在`references/watch-loop.md`中；如果此会话尚未加载它，请在执行操作之前阅读它。

**`trajectory`是事实，不是结论。你把它交给委托技能（叶子：`ce-debug`和`ce-resolve-pr-feedback`），他们判断收敛。**触发器是：`check_recur_max >= 2`； `stream_alternations >= 3`；上升 `unresolved_trend` 和 `new_threads_this_tick > 0` 穿过通道； `heads_since_progress >= 2`；或任何`invariant_rounds[].rounds >= 2`（2 个记录轮的密钥意味着下一个修复将是其第三个）。当轨迹与 1 相交时，将其传递给该蜱虫的 `ce-debug`/`ce-resolve-pr-feedback` 调用作为**强制输入** **在**该叶子突变之前，并让叶子决定这是普通进展还是真正的不收敛。然后，叶子可能会返回一个 `needs-human` 残差来停放*整个流*，例如紧急的 CI 权衡、错误方法的挑剔集群或第三轮不变。永远不要自己声明不收敛。触发→路由→停放→重开协议在`references/watch-loop.md`（**不收敛**）；如果此会话尚未加载它，请在执行此操作之前阅读它。

## 排序不变式（全文）

**排序不变式（这就是重点）：**

1. **先检查终端。** 如果`pr_state`为`MERGED`或`CLOSED`，则停车报告；循环完成。一个**例外**：当此运行刚刚完成对 PR 的授权 `stack-land` 合并时，将该 MERGED 结果视为托管堆栈层转换（请参阅步骤 3 的堆栈着陆步骤），而不是运行级别的终端停止。
2. **立即捕获头部 SHA**（`git rev-parse HEAD` 或快照的 `head_sha`），以便您稍后可以判断评论是否已推送。

**托管堆栈预推送基线。** 在调用可能将活动目标推送到已确认的托管堆栈中的委托之前，记录来自新`gh stack view --json`的可恢复基线：管理者命令的位于目标或目标之上的开放分支（目标及其开放依赖项）以及跟踪远程上每个分支的当前远程跟踪 OID。需要 target/current 分支有一个干净的工作树和仍然确认的经理成员资格。如果任一前提条件失败，则停止每种模式下的主动调用：不调用委托、运行另一个tick或arm/re-arm观察者；陈述残差并给出主机渲染的恢复调用。不要因为缺少原子多引用推证明而停止；当前`gh stack push`可以非原子地更新分支（`github/gh-stack#216`）。当安装的管理器稍后证明原子推送时，更喜欢全有或全无，但总是在推送后重新探测而不是假设它。

3. **CI之前的反馈。**如果注意力集具有**未解决的线程**或**非线程反馈候选者（`counts.threads > 0`或`counts.comments > 0`），请在完整模式**与`mode:pipeline`**调用`ce-resolve-pr-feedback`**一次**。每个蜱虫一次解决通行证；切勿扇出多个。传递已解析的 PR 引用：快照的 `url` 中的基本 `[HOST/]OWNER/REPO#N` 或完整 PR URL。然后，分叉→上游PR针对**上游基础**进行解析，而不是分叉签出的`origin`，这会查询错误的PR命名空间。 `mode:pipeline` 使解析器返回任何 `needs-human` 作为结构化残差，而不是暂停在会导致手表停顿的阻塞用户问题上。解析器重新获取并判断“所有”反馈（内联线程、评论正文和顶级评论），并且在空时是幂等的。请求更改的审核正文或带有**无内联线程**的裸顶级“请重命名 X”仍必须触发通过。 **当上面的审查触发器被交叉时，传递`trajectory`**，这样解析器就可以判断跑步机或错误方法挑剔集群并返回一个方法级别`needs-human`，而不是永远修复； `invariant_rounds[].rounds >= 2` 触发器在该通道可能修复、提交或推送之前**路由它。 **当重复项目“有效”并共享一个根和修复时，请求进行有界类评估**，因此它将 PR 触及的等效站点合并到单个修复中，而不是每个头修复一个（`references/watch-loop.md`，非收敛）。

对于任何委托结果，通过一个共享步骤处理其类型化 `needs-human` 残差。立即渲染 `## Needs your decision` 下的每个完整负载，保留其不变以供调用者返回，并将其写入操作系统临时 JSON 文件。将每个残差保留一次：快照验证完整模式，冻结每个源的当前观察，并在锁定状态写入下发布一个决策。它在规范`needs_human_residuals`中发出未更改的有效负载，在`human_decisions`中发出其应答路由ID；来源处置仍然是普通的open/dispatched事实。任何覆盖的观察变化或消失都会使整个决定无效并重新激活其幸存的来源，但远程活动永远不是答案。继续独立工作而不解决被覆盖的线程。

在解析器之后，协调您传递的每个**注释，这些注释未被返回的类型残差**覆盖。顶级评论或评论主体永远不会自行退出提取，并且在应用代理判断后，`ce-resolve-pr-feedback`可能会默默地删除样板文件、状态噪音或其他不可操作的反馈。将您通过的每条评论标记为`dispatched`，除非共享残留标记已将其停放；切勿添加特定于路线的 `needs-human` 标记。不标记未覆盖的评论会将其保留在注意力集中，因此循环永远不会解决：

```bash
SKILL_DIR="<absolute path of this skill's directory>"; SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && chmod 700 "$SCRATCH_ROOT" || { echo "unsafe scratch root: $SCRATCH_ROOT" >&2; exit 1; }; STATE_DIR="$SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>"; (umask 077; mkdir -p "$STATE_DIR") || exit 1; chmod 700 "$STATE_DIR" || exit 1;
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pr-snapshot" mark --pr <N> --repo <[host/]owner/repo> --state-dir "$STATE_DIR" --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS" --disposition needs-human --residual-file <path-containing-one-exact-typed-residual>
"$PY" "$SKILL_DIR/scripts/pr-snapshot" mark --state-dir "$STATE_DIR" --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS" --comment <ID> --disposition dispatched --invariant-key <key-returned-by-the-leaf-on-a-fix-outcome>
```

如果已调度的线程标记报告不可用的基线，请拍摄新的快照。已解决的线程会退出；对于仍处于开放状态的回复，请在重试之前协调实际回复和任何后来的审查者评论。不要盲目地重新发布回复或将较新的请求标记为已处理。

在共享残差标记上传递`--pr`/`--repo`。 `mark` 然后在原子写入之前重新读取每个覆盖线程当前的最后一条评论（包括您刚刚发布的回复），因此稍后的审查者活动会重新打开整个组而不是被吞没。仅当重新阅读每个涵盖的主题时才会发布该决定；缺失的观察使完整的源集可操作。出于同样的原因，所涵盖的评论和评论机构保留其快照编辑身份。 **发送的评论**标记不需要基线：它会保持沉默，直到明确的 `mark --disposition open` 为止，并且永远不会通过正文编辑重新激活，因为状态机器人会在每次推送时重写其正文。真正的新请求以审阅线程或新评论的形式到达，两者仍然显示。在 **fix** 结果中，将叶返回的 `invariant_key` 保留在同一已调度标记上（`--thread` 或 `--comment` 加 `--invariant-key`）；当叶子没有返回时省略该标志。叶子不运行`pr-snapshot`。

当用户回答时，将他们的响应映射到显示的 `decision_id`，将准确的响应保存在文件中，并在执行操作之前记录共享的答案转换。仅当此标记成功时，答案才会被消耗。只读禁止执行转换，而不是渲染它。在只读运行（其边界禁止写入）中，返回下面的文字命令作为唯一的挂起转换；替换确切的已知值并为不可用的调用元数据或应答文件路径保留显式占位符。该呈现的命令必须包含文字 `--answer-decision` 和 `--answer-file` 标志。散文释义或内存状态移动是不完整的。

```bash
SKILL_DIR="<absolute path of this skill's directory>"; SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && chmod 700 "$SCRATCH_ROOT" || { echo "unsafe scratch root: $SCRATCH_ROOT" >&2; exit 1; }; STATE_DIR="$SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>"; (umask 077; mkdir -p "$STATE_DIR") || exit 1; chmod 700 "$STATE_DIR" || exit 1; RUN_INVOCATION_ID="<invocation_id>"; RUN_STARTED_AT="<invocation_started_at>"; RUN_BUDGET_SECONDS="<invocation_budget_seconds>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pr-snapshot" mark --state-dir "$STATE_DIR" --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS" --answer-decision <decision_id> --answer-file <path-containing-the-exact-human-response>
```

下一个快照返回 `answered_human_decisions` 中的记录，并使每个仍然匹配的源成为普通的可操作工作。应用答案，然后使用现有的dispatched/confirmed标记；当其来源被处理或他们的观察发生变化时，已答复的记录将被淘汰。切勿将线程回复、评论编辑、检查重新运行、头部移动或货币更改隐式转换为答案。

在步骤 4（报告）中展示这些决定并继续独立工作。一旦没有剩余，`mode:pipeline`返回规范集作为其决策切换；交互式连续模式持续监视停放的信号源周围。还要保留解析器的 **非常规结论** 作为第 4 步摘要：与审查者建议的修复方式不同的修复 (`fixed-differently`)、拒绝的反馈 (`declined`) 或被反驳为错误的反馈 (`not-addressing`)。普通的`fixed`很日常，不值得携带。
4. **过时的 SHA 取消。** 将当前的头 SHA 与步骤 2 中捕获的 SHA 进行比较。如果它**更改**，则评论传递（或其他人）会推送，因此此快照中的 CI 失败是针对死 SHA 的：**不要对其采取行动**。新的运行将在下一个刻度出现。如果**没有**改变，请继续CI。
5. **当前头上的CI。**将*所有*可操作的失败检查聚合到一个修复过程中；不要按支票发送。从元数据分类：
   - **Flaky/infra**（已知不稳定作业，infrastructure/timeout信号）→从失败检查的`details_url`（`https://<host>/<owner>/<repo>/actions/runs/<run-id>/…`）中提取运行ID **和完整的基础存储库（包括主机**）并运行`gh run rerun <run-id> --failed -R <host>/<owner>/<repo>`。如果没有运行 ID，`gh run rerun` 将打开一个交互式运行选择器，该选择器会阻止无人值守的运行。 fork→upstream 和 GitHub Enterprise PRs 需要主机限定的 `-R`：运行位于其自己主机上的 **base** 存储库中，因此裸露的 `-R <owner/repo>`（或没有 `-R`）以 fork 或默认的 `github.com` 和 404 为目标。
   - **被存储库设置或权限阻止**（日志显示 GitHub 由于存储库或令牌的配置方式而拒绝操作，而不是因为代码 - 例如自动合并作业失败，并显示“此存储库不允许自动合并”）→ 不调用 `ce-debug`；任何代码更改都无法修复它，并且更改设置超出了该技能的权限。设置修复后，仅重新运行该作业，而不是运行中的每个失败作业：像 flaky/infra 项目符号那样获取 `<run-id>` 和存储库，使用 `gh run view <run-id> --json jobs --jq '.jobs[] | {name, databaseId}' -R <host>/<owner>/<repo>` 查找作业的 `databaseId`（检查浏览器 URL 中的作业编号是不同的 ID 和 404），然后运行 `gh run rerun --job <databaseId> -R <host>/<owner>/<repo>`。如果它现在已经读取固定（对于自动合并，`allow_auto_merge`是`true`），请在这个时间点重新运行它。否则，编写一个类型化的 `needs-human` 残差，其 `sources` 是该检查，其 `decision_context` 命名设置或权限及其更改位置，通过上面的共享残差步骤将其保留，并在用户回答已修复时重新运行。切勿推送空提交或任何其他新头来重新触发它。
   - **真正的 test/build 失败** → 调用 `ce-debug mode:pipeline` 一次，以失败的作业及其日志尾部为种子。 **当上面的CI触发器被交叉时，同时传递`trajectory`（`recurring_checks`，`check_recur_max`，`heads_since_progress`），以便判断振荡与普通进度。**其结构化返回`status`恰好是`fixed-and-pushed`，`fixed-not-pushed`，`flaky-infra`之一， `diagnosed-no-fix`，或`needs-human`；不要发明`infra-retry`或`stale`。一次没有返回就结束的传球，即使是推送的传球，也会被处理为 `diagnosed-no-fix`。不要从它运行的命令猜测它的状态；下一个快照显示了任何推送的更改。像以前一样处理收敛修复并重试。保留返回结果中的任何非空 `prevention_signal` 用于第 4 步摘要；这是一个建议，所以不要实施它。也为步骤 4 摘要保留 `diagnosed-no-fix` 返回的 `summary` 及其红色残差，因为它可能是已修复故障的开放 PR 的唯一命名位置。 `needs-human`结果返回完整的类型化残差，其`check`源通过上面的共享残差步骤进入规范集；将这些支票存放在相同的残留文件中。 `diagnosed-no-fix` 和失败的推送仍然是普通的红色残差。切勿削弱测试、变基、重置或强制推送来清除它们。
   上面的共享残差步骤已经停放了由 `needs-human` 残差覆盖的每个检查。记录您执行的每个其他检查，以便不会在此头重新分派（重新设置内联变量）：

   ```bash
   SKILL_DIR="<absolute path of this skill's directory>"; SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)"; [ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && chmod 700 "$SCRATCH_ROOT" || { echo "unsafe scratch root: $SCRATCH_ROOT" >&2; exit 1; }; STATE_DIR="$SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>"; (umask 077; mkdir -p "$STATE_DIR") || exit 1; chmod 700 "$STATE_DIR" || exit 1;
   PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
   "$PY" "$SKILL_DIR/scripts/pr-snapshot" mark --state-dir "$STATE_DIR" --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS" --check "<key>"
   ```

   （新的头 SHA 会自动清除这些。）

6. **分支货币和冲突（第三个流 - 在评论和 CI 之后）。** 消耗确切的当前 `branch_currency` 项目；没有项目意味着没有碱基到头部的突变。完整的路线、索赔生命周期和`BEHIND`/`DIRTY`机制都在`references/branch-currency.md`中。
7. **在已确认的托管堆栈中进行授权目标头推送后，在恢复监视之前保留上堆栈**（`gh stack rebase "<first-dependent-branch>" --upstack --no-trunk` + `gh stack push`；冲突时中止并停放）：`references/stack.md`。
8. **任何突变后，在下一个tick开始时重新快照**，传递相同的`--invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS"`。头部 SHA 和 CI 宇宙已经改变，但调用范围的预算没有改变。不要运行第二个 `snapshot` 中间刻度来重新导出 CI；这就是导致陈旧 SHA 混乱的原因。

在接受的托管堆栈延续期间，有一个观察者（通过 `--downstack-pr` 探测较低层）和一个变异目标；转移条件、返回规则和着陆门在`references/stack.md`中定义。
