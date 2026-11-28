# 步骤一详情：伪造检查、PR解析、链分类、结账、观看模式

## 先决条件

该循环针对具有文件系统访问权限的本地结帐运行 `gh`、`git` 和捆绑的 Python 帮助程序。没有这些（一些沙盒 GUI 环境）的宿主无法运行此技能 - 说出来并停止而不是半运行。

## 步骤1：确认GitHub，解析PR，选择执行模式

**仅GitHub。** 这项技能及其代表的一切都代表讲GitHub的API（`gh`，审查线程，操作）。首先确认仓库位于GitHub：`gh repo view`成功是积极信号（它还涵盖`gh`配置的GitHub企业）。如果失败，请检查远程 — `git remote get-url origin` 指向 `gitlab.*` 主机表示 GitLab，`bitbucket.*` 表示 Bitbucket。在任何非GitHub伪造（git托管服务）上，或者如果`gh`根本无法解析存储库，**停止并告诉用户ce-babysit-pr仅是GitHub**并且尚不支持GitLab/other伪造。不要继续进行会产生混乱错误的 `gh` 调用。

然后从参数 (number/URL) 或当前分支解析目标PR。如果不存在打开的PR，则报告并停止。使用 PR 解决草稿状态。对于没有显式用户监视模式令牌的自动呼叫技能切换，此检查必须是纯读 `gh pr view --json isDraft`，在任何引导程序之前运行 - 绝不是 `snapshot --start-invocation`，这会创建新的调用并取代用户在该草案上明确授权的监视。草稿目标报告其草稿状态，并在任何引导程序或观察者之前根据“草稿 PRs 是选择加入”边界在此停止。在用户调用的运行中，第一个快照发出的 `pr_is_draft` 用作正在进行的信号。

**在观看 CI 之前检查自动合并是否可以启动。** 当 PR 期望自动合并时（对其进行检查以启动自动合并，或者用户或调用技能表示自动合并应该启动它） - 使用 `gh api repos/<base-owner>/<base-repo> --hostname <host> --jq .allow_auto_merge` 读取基础存储库的设置。如果是`false`，则没有CI结果可以合并此PR：报告存储库设置设置>常规>拉取请求>“允许自动合并”已关闭，并在任何引导程序或观察程序之前停止。在 `mode:pipeline` 中，该报告是来自 `references/pipeline.md` 的结构化回报 `{ status: "needs-human" }`，其中一个残差的 `decision_context` 命名了该设置。更改设置是用户的决定，而不是该技能的决定。一旦打开，已经失败的自动合并检查将保持红色，直到重新运行其作业；勾选的第 5 步处理该问题。

**自动对目标的PR链进行分类；永远不要依赖用户宣布堆栈。** 第一个快照和以后的每个轮询都会使用 `gh stack view --json` 探测只读本地管理器，仅当其分支列表包含目标 PR 时才接受它。如果这无法证明成员资格，则帮助程序将使用只读 GraphQL 后备。成功的空栈意味着`pr_chain.manager_status == "absent"`。仅当单独的只读查找解析存储库的默认分支时，特定的堆栈字段模式不可用响应也意味着`"absent"`；身份验证、传输、速率限制、格式错误、其他 GraphQL 或失败的默认分支探测意味着 `"probe-error"`。当没有确认管理器时，普通的开放PRbase/head关系将独立的PR与手动依赖链区分开来。 Discovery 永远不会运行 `gh stack checkout`、导入堆栈、切换分支或更改远程状态。

**只有当新鲜快照有`manager_status == "confirmed"`时，堆栈范围的延续才会激活；没有其他分类授权它。** 手动依赖链永远不会激活堆栈范围的延续：即使其 base/head 拓扑类似于管理器的有序分支，也将其保持为目标本地。 `probe-error` 也保持目标局部性和变异保守性，直到后来的快照肯定地确认了管理者。 Discovery 仍然为每个PR 看护运行 — 状态不会禁用已确认的管理器检测或步骤 7 upstack 维护。

对于已确认的托管堆栈，在选择活动层之前检查管理器的有序条目一次；这是只读查看命令，不是多PR监控。在进行任何 review/CI 工作之前，按照`references/stack.md` 中的表格解决**姿势**。如果姿势仍然是`target`并且所请求的中间PR有一个未解决的downstack层，则提供一次从最低的未解决的非草图层开始并向上进行（`stack-ready`），仅目标作为替代方案；不要默默地将 review/CI 工作重定向到另一个 PR。如果姿势已经是 `stack-ready` 或 `stack-land` 并且请求的 PR 有一个未解决的下栈层，则从最低的未解决的非草图层开始，而不询问（下栈到上栈）。如果所有下层都已解决，则从请求的 PR 开始。当请求的 PR 看起来已经准备好或稍后稳定在 `target` 之下时，如果需要工作，则提供一次继续立即打开的非草稿上栈层（接受选择 `stack-ready` 进行其余的运行）。这一一次性提议扩大了已确认的托管堆栈的PR 看护范围 - 它**不是**创建或采用 PR 堆栈的主动建议。托管托管堆栈的显式请求算作 `stack-ready` 接受，因此不要多余地请求。在无法请求的`mode:pipeline`中，仅当调用已提供`posture:stack-ready`、`posture:stack-land`或等效的堆栈范围范围时，才继续超出所请求的PR；否则返回下一个候选者作为残差。

一旦`stack-ready`或`stack-land`生效，该姿势授权依次照顾已确认的托管堆栈的每一层，而无需在每一层再次询问。保持 1 个活跃的 PR 目标和 1 个观察者。在每次转换时：重新验证管理器成员身份和有序状态，停止旧观察者，switch/check退出下一个直接层，然后使用`--continue-invocation`初始化其自己的快照状态以及第一个快照使用的标志上相同的三个记录值 - `--invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS"`（锚标志是`--session-started-at`，而不是`--invocation-started-at`） - 加上`--continue-dead-time-seconds <prior layer's `invocation_dead_time_seconds`>`，因此共享活动时间预算包含已在早期层中排除的挂起时间（每个层的状态目录会累积其自己的死区时间，因此如果没有此功能，新层会将先前的挂起视为活动状态） - **并在继续调用时重新声明相同的 `posture:` 值**。调用预算不会按层更新。除非用户明确包含该草稿，否则切勿跳过草稿或输入该草稿；切勿通过带有 `needs-human` 阻挡层的层。停在范围之外、人为阻挡层、堆栈末尾、预算或用户停止的初稿处。在每次跨PR转换之前重新确认`manager_status == "confirmed"`——失去肯定确认会结束堆栈范围的延续，而不是降级为手动链行为。

**旧-PR摄入量在结帐门之前进行。** 在新调用时，在此处运行`references/intake.md`。它的评估只是读取，所以你无法推动的PR仍然会得到一个判决；返工或关闭判决在任何快照或观察者之前停止（或返回，在 `mode:pipeline` 中）。用户请求接管 PR 的请求会转到 `references/takeover.md` 而不是下面的门。

**在任何委托突变之前验证本地签出是 PR 的头 *分支*。** `ce-resolve-pr-feedback` 和 `ce-debug` 提交并推送 **当前签出的分支** - 因此，不是 PR 的头分支的签出会使他们的修复无法推送或落在错误的分支上。匹配的 `HEAD` **SHA 是不够的**：分离的 HEAD 或恰好指向 PR 头 SHA 的*不同*本地分支通过了 SHA 检查，但仍然无法推送 PR 的分支。因此，验证结帐实际上是在 PR 的头 **ref 上，并具有匹配的上游**：解析 `gh pr view <ref> --json headRefName,headRefOid,isCrossRepository`，并确认 `git branch --show-current` 等于 `headRefName`（上游跟踪 PR 头存储库）。健壮的默认设置是**在变异之前运行`gh pr checkout <ref>`（它检查头分支并设置跟踪，并处理它可以推送到的分叉头）。在已确认的托管堆栈中，改为运行 `gh stack checkout <PR number>`。它将堆栈从 GitHub 拉下来。在 `gh pr checkout` 重新结帐后，本地经理不知道分支，因此 `gh stack view` 失败并显示“不是堆栈的一部分”，并且每个需要它的配方也会失败。如果你不能 - **无法推送访问 PR 的头引用**（当头存储库是你的，当你对其有写访问权限时，或者当 `maintainerCanModify` 为 true 时在其他人的分叉上时，你就拥有它）或脏签出 - **停止并告诉用户签出 PR 的分支**，而不是改变错误的分支。当阻止者是推送访问时，还提供接管（`references/takeover.md`）。将 *clean* 结账切换到 PR 的分支并不是询问的理由；做吧。照顾当前分支自己的PR（常见情况）已经满足了这一点。

然后决定**手表如何维持自身**——一旦回合结束，技能就无法被魔法重新调用，所以*你*设置循环。 **默认设置是一个自我维持的会话中手表：您不需要做一次勾选并交回恢复命令。** 在这里阅读 `references/watch-loop.md` 了解机制；后面的步骤引用其部分而不是重新阅读它。然后：

**用户可运行的恢复语法。** 每当此技能打印或复制恢复调用时，默认为`/ce-babysit-pr <url>`，并且当运行姿势不是`target`时，附加相同的`posture:stack-ready`或`posture:stack-land`令牌，以便检查点/持久/会话重新进入保持堆栈范围。仅当活动主机为 Codex 或明确记录以美元为前缀的技能调用时，才使用 `$ce-babysit-pr <url> [posture:…]`。仅将调用呈现为内联代码并仅输出一种形式。

- **自维持会话中监视（默认）。**持续监视，直到满足停止条件。默认情况下，运行确定性变化检测器`pr-snapshot watch`，并使用宿主工具等待其`BABYSIT_WAKE`输出。当主机指令规定PR如何等待工作时，主机的机制将取代检测器（`references/watch-loop.md`，**选择唤醒源**）。检测器轮询无需代理令牌；每次唤醒都会将控制权返回给该代理，以进行一次判断和子技能调用。探测器在每次唤醒时退出，因此在滴答声后重新启动它。切勿将这些判断折叠到 shell 脚本中。 `references/watch-loop.md` 定义调度和唤醒处理。
- **检查点。** 仅当用户请求或没有任何东西可以唤醒此代理时才使用检查点模式。只运行一次，持久化，报告并打印恢复调用。假设监控已暂停。切勿伪造带有前景 `sleep` 的循环，或结束回合并承诺在没有唤醒源的情况下继续。
- **管道**（`mode:pipeline`，由像`lfg`这样的编排器设置） - 内联运行**有界同步滴答**：编排器是调度程序，因此循环自己进行滴答（快照→执行→重新快照）直到**管道停止**（步骤3），然后返回。完全非交互。请参阅 `references/pipeline.md` 了解不同之处 — 不同的停止条件、结构化结果中返回的残差以及结构化返回 — 并阅读 `references/watch-loop.md` 了解其边界。

**耐用性。** 会话中的手表受会话限制；如果会话关闭，则使用主机渲染的恢复语法重新调用会干净地恢复（状态完全保留在磁盘上）。对于必须比会话（天）更长的无人值守监视，请转移到存在持久调度程序的地方 - Grok `scheduler_create --durable`，或运行 `<harness-cli> exec '<host-rendered resume invocation>'` 的 cron - 接受新的无头运行从磁盘重建并丢失此对话的上下文（保留相应的决策，因此不会重新诉讼）。如果用户通过了某种模式，则尊重它；否则，选择每个宿主功能，在一行中说明，然后继续。
