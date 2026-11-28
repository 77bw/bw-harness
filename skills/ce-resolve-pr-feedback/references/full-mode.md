# 完整模式

当模式检测（在 SKILL.md 中）路由到 **完整模式** 时，请阅读此参考资料 — 未给出参数、提供了 PR 编号或提供了完整的 PR URL（`.../pull/N` 无注释片段）。完整模式处理 PR 上所有未解析的线程。当参数是 PR URL 时，解析主机、`OWNER/REPO` 和其中的数字 — 主机提供下面的 `GH_HOST` 前缀，而 `OWNER/REPO` 则针对分叉→上游 PR 的正确存储库。

形状：**一次获取，集中判断，仅针对修复分派子代理。** 作为编排者，您可以在一次获取中保留每个线程，因此您可以在自己的上下文中判断有效性，您可以在其中读取每个文件一次，发现跨多个线程出错的审查者，并权衡作者的设计意图。仅派遣子代理来“实施”您已批准的修复。不要委托判断：每个线程的子代理会支付每个代理的开销，重新读取相同的文件，并丢失跨线程视图，即使对于结果被跳过的线程，您也会付出代价。

## 1. 获取未解决的线程

如果没有提供PR号，则从当前分支检测：
```bash
gh pr view --json number -q .number
```

然后使用 [scripts/get-pr-comments](../scripts/get-pr-comments) 处的 GraphQL 脚本获取所有反馈。将 `SKILL_DIR` 设置为您加载 ce-resolve-pr-feedback SKILL.md 的绝对目录 — Bash 工具的 CWD 是用户的项目，而不是技能目录，并且 shell 状态在 Bash 调用之间不会持续存在，因此将其内联设置在下面运行捆绑脚本的每个块中。如果磁盘上缺少捆绑脚本，则调用显然会失败；回退到此块之后显示的 `gh` 命令。

**GitHub 企业主机。** 除非另有说明，否则捆绑的 `gh api graphql` 脚本会命中 `gh` 的默认主机，因此在 GHE PR 上，它们会错误地定位`github.com`。导出主机：如果调用者传递了完整的PR **URL**，则获取其主机；否则从`gh repo view --json url -q .url`读取。然后，因为 shell 状态在单独的 Bash 调用之间**不会**持续存在，所以将主机作为 `GH_HOST=<host>` **env 前缀内联传递到每个捆绑脚本调用**（`gh api` 尊重 `GH_HOST` 作为请求主机）。一个块中的单个 `export` **不会** 携带到作为后续 Bash 调用运行的 reply/resolve/verify 块，这就是为什么下面的每个调用都显示前缀。在 `github.com` 上，完全删除 `GH_HOST=<host> ` 前缀。

```bash
PR_HOST=$(printf '%s' "<pr-url-if-one-was-passed>" | sed -n 's#^https\?://\([^/]*\)/.*#\1#p');
[ -z "$PR_HOST" ] && PR_HOST=$(gh repo view --json url -q .url 2>/dev/null | sed -n 's#^https\?://\([^/]*\)/.*#\1#p');
echo "$PR_HOST"   # github.com -> no prefix; any other host -> prefix GH_HOST=<host> on each script call below
```

```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/get-pr-comments" PR_NUMBER OWNER/REPO   # omit GH_HOST=<derived-host> on github.com
```

**传递基数 `OWNER/REPO`** （当给出一个时，从 PR URL 解析）作为第二个参数。否则，`get-pr-comments`会在*当前签出*中回落到`gh repo view`——因此，对于以 URL 形式提交的分叉→上游 PR，省略它将从分叉（或失败）而不是上游基础存储库获取审核反馈。下面的每个`get-pr-comments`调用（获取和验证）都采用相同的`OWNER/REPO`。

返回带有这些键的 JSON 对象：

| 钥匙 | 内容 | 有file/line吗？ | 可以解决吗？ |
|-----|----------|---------------|-------------|
| `pending_review` | 您对此 PR 或 `null` 未提交（待处理）审核的节点 ID | n/a | n/a |
| `review_threads` | 未解决的内联代码审查线程（包括过时的）；每个包装器都携带 `root_comment_id` 用于 REST 回复，每个节点携带其 GraphQL 线程 ID 用于解析 | 是的 | 是（GraphQL） |
| `pr_comments` | 顶级PR对话评论 | 不 | 不 |
| `review_bodies` | 使用非空文本审核提交正文 | 不 | 不 |
| `pr_author` / `viewer` | PR作者登录和代理账号登录，用于第2步判断身份 | n/a | n/a |

**三种反馈都在范围内。** `review_threads`、`pr_comments`、`review_bodies`与步骤3中的判断方式相同；只是回复和解决机制不同（步骤 7）。提取不排除任何基于谁编写的内容 - 来自 PR 作者的顶级评论是人类要求对代理打开的 PR 进行更改的普通方式，因此它是与其他反馈一样的反馈。

**如果 `pending_review` 非空，则在此停止。** 当您持有未提交的审阅时发布的线程回复将被吸收到该草稿中：回复调用会返回评论 ID 和 URL，就好像成功一样，但在提交草稿之前，审查者看不到任何内容。不要继续执行步骤 2-8——修复程序将会落地，而每个回复都会悄然消失。告诉用户他们对 PR 有一条未提交的评论，必须先提交或放弃该评论，然后此技能才能回复，然后停止。请勿自行提交或丢弃；审查草案是未发送的人类写作。

如果脚本失败，则回退到：
```bash
gh pr view PR_NUMBER --json reviews,comments
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments
```

## 2. 分类：将新的与待处理的分开

在处理之前，协调每条反馈的回复和解决状态。

**审查线程**：只有当一个普通处理的线程同时具有可见的、已提交的实质性回复和权威的线程解决方案时，该线程才是完整的。独立协调这些条件：

- 明确推迟人类选择的回复（例如，“需要对此进行调整”、“要考虑这一点”或没有决定的选项）是**待决的决定**。保持线程打开并且不要重新处理它。
- 在线程仍处于打开状态时记录已完成的修复或回复判决的回复是**待解决**。请勿重新发布回复或重新应用修复；将现有的可见回复带到步骤 7，并在待审核状态为空后仅完成缺少的解决方案。
- 没有任何一种实质性响应的线程是**新的**。

**PR 评论和审查机构**：这些没有解析机制，因此它们在每次运行时都会重新出现。按顺序应用两个过滤器：

1. **可操作性**：当某人对此 PR 提出开放请求时，该项目是可操作的：需要修复、回答或决定的内容。该过滤器还可以防止运行在其自己的输出上循环。本次运行或之前的运行发布的回复是处理记录，而不是请求，因此它会放置在此处，无论它报告修复还是携带暂停的 `needs-human` 决策。该停放的物品本身已被跟踪；重新阅读自己的文章作为新的反馈是循环永远不会解决的方式。谁发布的项目永远不会决定这一点，包括打开PR的帐户。示例：审阅包装文本（“这里有一些自动审阅建议...”）、批准（“这看起来很棒！”）、状态徽章（“已验证”）、CI 摘要（无后续询问）。如果没有什么需要解决、回答或决定的，那么它就不是可操作的——完全将其从计数中删除。
2. **已回复**：对于可操作的项目，请检查 PR 对话以获取引用并解决反馈的现有回复。如果回复已存在，请跳过。如果没有，那就是新的。

区别在于内容，而不在于谁发布了什么。队友的推迟、之前的技能运行或手动回复都算在内。同样，可操作性与内容有关——请求特定代码更改的机器人反馈是可操作的；机器人的样板标头包装这些请求不是。

**无声掉落。** 不可操作的物品会在没有旁白的情况下掉落。请勿在对话、任务列表或第 9 步摘要中宣布、列出或计数已删除的项目。来自 CodeRabbit、Codex、Gemini Code Assist 和 Copilot 的审阅机器人包装器（如“这里有一些自动审阅建议...”之类的正文）通常出现在此处 - 通过其样板内容识别它们，然后默默地丢弃。获取脚本仅过滤掉空白主体。每个作者和每种类型的反馈 - PR 作者、CI/status 机器人（例如 Codecov、审阅机器人）都会经过此内容检查，因此重复使用的帐户或更改的格式无法默默隐藏可操作的反馈。

如果所有反馈类型中都没有新的或待解决的项目，请跳过步骤 3-8 并直接转到步骤 9。如果仅保留待解决的线程，请跳过步骤 3-6 并直接转到步骤 7。

## 3. 巩固和决定（合法性门）

这就是决定有效性的地方。在发送任何修复之前，请在您自己的上下文中判断这里的每个**新**项目。立即将 [references/evaluation-rubric.md](evaluation-rubric.md)（立即阅读）中的标题应用于整个批次。当调用携带 `trajectory` 时，在分派任何内容之前在 [references/pipeline-mode.md](pipeline-mode.md) 中应用非收敛测试 - 演示的共享根在根处回答一次，而不是修复每个实例。

通过处理完整的集合，您可以完成每线程子代理无法完成的任务：
- **Dedup 按文件读取** — 读取一次文件并一起判断其所有线程。
- **跨项目推理** — 通过根假设聚类结果；一个来源（通常是机器人）在一个地方出错，就会在其兄弟姐妹中受到怀疑；来自独立审查者的一致请求是一个强烈的修复信号。
- **选择性深度** — 清晰的 nits 只需要注释加上 diff 行；仅在发现有争议或代码看起来是经过深思熟虑的情况下才进行深度阅读（调用者、不变量、`git blame`/PR作者意图的基本原理）。对有争议的少数派的深入阅读，才能抓住自信错误的审稿人。

对每个项目生成一个判决并排序为三个列表：

- **修复列表** — `fixed` / `fixed-differently`。这些将在第 4 步中分派给修复程序。对于每个，请记下 file/location（对于过时的线程，已解析的位置或锚点）和一行“要更改的内容”。 **类修复：**当跨项目传递（标题：“经过验证的发现可以跨越此PR本身引入的站点”）找到此PR接触的等效相同不变站点时，将它们记录为**一个**修复列表项，枚举每个具体位置（`file:line`）并列出它涵盖的每个反馈ID - 一个类项目→一个修复程序（步骤4），因此站点被连贯地编辑并且每个覆盖thread/comment 是根据该单个结果进行回复和解决的。仅列举处理明确的站点；需要自己判断的网站仍然是一个单独的项目。
- **回复列表** — `replied` / `not-addressing` / `declined`。没有代码更改。现在根据标题撰写回复文本（您有证据）并将其进行到步骤 7。
- **人类列表** — `needs-human`。现在编写 `decision_context` 并对每个需要判断的项目运行标题的“升级前判断”步骤；做出的裁决会将该项移至其指定的列表中，其余的则进入步骤 7 和 9。

创建所有新项目的任务列表（例如，Claude Code中的`TaskCreate`，Codex中的`update_plan`），并标记其结论，以便进度可见。

**大规模。** 如果批处理很大（许多线程跨越许多文件）并且判断它们全部内联会溢出您的上下文，请按组处理合并（例如，约 8-10 个线程的文件集群组），并增量地发出三个列表。不要将判断分散给子代理来避免这种情况——而是分批进行。

如果修复列表为空（所有判定均为 reply/needs-human），则跳过步骤 4-6 并转到步骤 7。

## 4. 修复（仅限修复列表）

**仅**针对修复列表项目派遣修复程序。回复列表和人工列表项目永远不会到达子代理。

### 每个修复运行的位置

第 3 步已经阅读了每个修复列表项背后的代码。当项目形成真正的并行批次（不相交文件上的两个或多个项目）时，或者对于其修复范围远远超出您所阅读的内容的项目（跨调用者的重命名、多个站点的类修复）时，调度修复程序。应用此上下文中的所有其他项目，并使用下面的修复程序提示作为您自己的说明。

每个修复列表项都以下面的返回格式中的一个**每项结果** 结尾，无论是修复程序生成的还是您生成的。此运行的 **更改集** 是这些结果 `files_changed` 的并集。步骤 5-7 只读取每个项目的结果和更改集，而不读取生成它们的路径。

### 派遣

阅读 [references/agents/pr-comment-resolver.md](agents/pr-comment-resolver.md) 并为您委托的每个修复列表项生成一个通用子代理，该子代理以该修复程序提示为种子。不要在 type/name 之前派遣独立代理。 Fixer只实现：有效性判断已经完成，所以实现并返回；它不会重新判断修复是否值得。

每个修复者都会收到：
- feedback_id（话题 ID 或评论 ID）和反馈类型。
- 文件路径和位置字段：`line`、`originalLine`、`startLine`、`originalStartLine`（对于过时的线程，从步骤 3 解析location/anchor）。
- 审稿人的评论文本。
- 您的第 3 步注意事项：要更改的内容以及为什么它被判定为有效。
- PR数字。

对于 `pr_comment` / `review_body` 修复列表项（无 file/line），修复程序从注释文本和 PR 差异中识别相关文件。

**没有子代理功能 - 您自己按顺序应用修复。** 当宿主无法显示调度（或调度失败）时，在此上下文中一次处理修复列表中的一项，使用修复程序提示作为您自己的指令并生成相同的每项结果。这是一条受支持的路径，而不是报告为覆盖范围丢失的缺陷：关于每个项目是否有效的决定已经在步骤 3 中发生，并且修复程序仅“实施”您批准的更改，因此在这里运行它们会消耗并行性和上下文空间 - 而不是正确性。保持调度路径的规则：一次一项，在编辑之前重新读取每个文件，如果实施发现矛盾，则停止重新评估（`blocked`处理不变）。您在这种情况下选择应用的项目遵循相同的规则。

因此，该技能不依赖于代理工具授权来完成审核。这是故意的：它在 `ce-babysit-pr` 下无人值守地运行，其中权限提示会停止整个循环，因此它需要很少的工具，并且仍然可以在不调度的情况下修复。

### 每个项目的结果格式（固定或内联）

- **结论**：`fixed`、`fixed-differently`或`blocked`
- **feedback_id**, **feedback_type**
- **reply_text**：Markdown 回复帖子（引用相关反馈）— `blocked`省略
- **files_changed**：已修改的文件列表（`blocked`为空）
- **原因**：做了什么，或者`blocked`的具体矛盾

**处理`blocked`。** 仅当实施揭示了修复程序可以看到而您无法看到的具体矛盾时，修复程序才会返回`blocked`（更改破坏了它可以看到的caller/test，或者代码不是所描述的结果）。使用该证据自行重新评估：要么重新发送更正的指令，要么将其移至回复列表 (`not-addressing`/`declined`) 或人工列表。不要默默地丢弃它。

### 批处理和冲突避免

**批处理**：如果委派 1-4 个项目，则并行调度所有项目。对于 5 岁以上的儿童，以 4 人为一组进行批处理。

**避免冲突**：接触同一文件的两个修复程序不会并行运行。您已经从第 3 步知道了目标文件 - 序列化共享文件的修复程序（分派一个，等待，然后下一个）；不重叠的项目并行运行。对于**类项目**，向修复程序提供其完整的枚举位置集和每个覆盖的反馈 ID（不是单个线程），并在此检查中考虑其**所有**站点 - 涉及另一个修复程序也涉及的文件的类修复程序必须针对每个文件进行序列化。当一个修复程序处理同一文件上的多个线程时，它会按顺序对它们进行寻址。

**顺序回退**：不支持并行调度的平台顺序运行修复程序。

修复有时可能会超出其引用的文件范围（例如，重命名方法会在其他地方更新调用者）。这种情况很少见，但可能会导致并行固定器发生碰撞。第 5 步（组合验证）捕获测试破损；第 8 步（验证）捕获未解决的线程。如果其中任何一个显示不一致的更改，请按顺序重新运行受影响的修复程序。

## 5. 验证组合状态

如果更改集为空，请跳过步骤 5 和 6 并继续执行步骤 7。

每个修复仅针对其自身的更改运行有针对性的测试。此步骤针对组合差异运行项目的完整验证**一次**，以捕获目标运行无法看到的修复之间的交互。

1. **运行项目的验证命令**（测试套件、类型检查或项目的活动约定指定的任何内容）。运行一次，而不是每个代理。

2. **绿色** -> 继续执行步骤 6。

3. **红色，失败涉及更改集中的文件** -> 一次内联诊断和修复过程。重新运行验证。如果仍然是红色，则使用包含测试输出的 `needs-human` 项目升级； **不要**提交。

4. **红色，失败仅影响更改集之外的文件** -> 视为预先存在。继续执行步骤 6，但在提交消息中添加页脚：`Note: pre-existing failure in <test> not addressed by this PR.`

记录第 9 步摘要的验证结果（命令运行、pass/fail 计数、记录的任何预先存在的故障）。

## 6. 提交并发布

仅提交更改集，保留树和索引中不相关的工作，并带有引用 PR 的消息：

```bash
git add [files in the change set]
git commit -m "Address PR review feedback (#PR_NUMBER)

- [list changes from per-item results]" -- [files in the change set]
```

在`mode:return-to-caller`中，捕获组合的修复提交SHA并按照[references/return-to-caller.md](return-to-caller.md)保存每个判断的操作和预期的检查清单标记。保存后返回；请勿为此批次的任何部分推送或输入步骤 7-8。失败的提交或保存会报告实际的本地状态和不完整的切换，永远不会完成。

普通和管道执行在远程尾部之前发布提交：
```bash
git push
```

在按下之前立即读取PR的状态。如果它不再打开，则表示在该批处理运行时发生了合并或关闭：不要推送，并将修复报告为未发布的本地提交以及未解决的项目。

## 7. 回复并解决

仅当发布批次的修复提交或批次未创建任何代码更改时，才输入远程尾部。返回调用者批次，并在步骤 6 处固定停止；他们保存的仅限回复和人员列表项目也仍然被推迟。无更改返回调用者批次使用此现有协议，即使写入失败也可以保存观察到的进度。 Resume仅通过[references/resume.md](resume.md)中的发布和协调条件进入此处，使用保存的判决和精确回复正文，并在完成或停止远程尾部后返回此处。在入口点的发布条件下应用合格的PR清单勾选。

普通评审帖的完成条件是一个可见的、提交的实质性回复加上权威的决议；独立地满足每个条件，并且永远不会重复满足的一半。发布每个新处理的项目：修复列表项目使用每个项目结果中的 `reply_text`；回复列表和人员列表项目使用您在步骤 3 中编写的回复文本。 **类项目** 携带多个涵盖的反馈 ID（来自其修复程序的`feedback_ids`/`feedback_types`）-回复并解决*每个*，在每个线程上发布共享的`reply_text`，而不仅仅是第一个；未解决的已覆盖线程在下一个`ce-babysit-pr`循环中再次显示为新工作。该机制取决于反馈类型。

### 回复格式

所有回复都会引用原始反馈的相关部分以保持连续性 - 具体的句子或段落，而不是整个评论（如果评论很长）。每个判决模板位于 [references/evaluation-rubric.md](evaluation-rubric.md)（跳过判决）和 [references/agents/pr-comment-resolver.md](agents/pr-comment-resolver.md) (`fixed` / `fixed-differently`)。

对于 `needs-human` 判决，发布听起来自然的回复，但不要解决该线程。让它保持开放状态以供人工输入。

### 评论主题

对于每种调用方式，选择第一个不满足的完成条件后再进行操作。没有可见的已提交实质性回复的线程运行步骤 0-4。 `resolution-pending`线程仅跳过步骤1，使用其现有的回复ID进行步骤2，并运行步骤2-4；不要判断、修复或再次发布。 `needs-human` 线程在其可见的提交回复后停止并保持未解决状态。

当前GitHub状态的决定与本地进度无关。在帮助程序的待审核检查失败之前或在写入检查点之前，POST 可能会成功。在重试之前协调现有回复及其提交的可见性；采用经过验证的回复而不是转发，并单独验证权威解决方案。

0. **回复前请验证线程 ID**。 GitHub Enterprise 可能会根据查询路径的不同，为同一线程返回不一致的节点 ID。请始终使用 [scripts/get-thread-for-comment](../scripts/get-thread-for-comment) 和评论的数字 URL ID 确认来自 `get-pr-comments` 的 ID 解析为正确的线程。从评论 URL 中提取数字评论 ID（例如 `discussion_r2589700` → `2589700`）以用于 `gh api` 调用；如果捆绑的脚本丢失，请使用 `gh api` 检查审阅线程：
```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<derived-host> GH_REPO=OWNER/REPO gh api repos/{owner}/{repo}/pulls/comments/COMMENT_ID --jq .node_id
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/get-thread-for-comment" PR_NUMBER COMMENT_NODE_ID OWNER/REPO
```
返回的 `id` 是用于解析的权威线程 ID，`root_comment_id` 是 REST 回复的线程第一条评论的数字 ID。如果线程 ID 与 `get-pr-comments` 返回的不同，请使用此脚本中的 ID。

1. **使用 [scripts/reply-to-pr-thread](../scripts/reply-to-pr-thread) 通过 REST 直接回复根评论。如果缺少捆绑脚本，请使用相同的 `POST repos/{owner}/{repo}/pulls/PR_NUMBER/comments/ROOT_COMMENT_ID/replies` 端点。不要替换`addPullRequestReviewThreadReply`、`gh pr review`或`/reviews` POST：这些操作会经历审核-提交状态，因此回复可以未提交，而成功的回复必须立即提交并可见。
从私有操作系统临时文件中提供主体。对于一个新的回复，下面引用的heredoc编写了多行Markdown而不需要shell扩展；切勿使用 `echo "..."` 或 `printf` 来解释转义序列。对于保存的回复，请使用工具将其精确解码的 `reply_body` 字节写入该文件，而不是运行说明性的heredoc，这会添加终端换行符。保留所有现有换行符，包括终端换行符：
```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
REPLY_BODY_FILE="<absolute private OS scratch reply file>";
cat > "$REPLY_BODY_FILE" <<'EOF'
> the specific sentence being addressed from the reviewer's comment

Fixed in abc1234 — the lookup now null-checks before dereferencing.
EOF
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/reply-to-pr-thread" PR_NUMBER ROOT_COMMENT_ID OWNER/REPO < "$REPLY_BODY_FILE"
```
如果 POST 后可见待审核，则帮助程序将以非零值退出。停止而不解决该错误；不要提交或放弃评论。在继续之前，请检查返回的评论 URL 是否包含正确的 `OWNER/REPO` 和 PR 编号。

2. **在解决之前验证 REST 创建的回复是否可见并已提交**。从返回的 URL 片段 (`#discussion_r2589700` → `2589700`) 中获取其数字 ID，并读回 GitHub 存储的内容：
```bash
GH_HOST=<derived-host> GH_REPO=OWNER/REPO gh api repos/{owner}/{repo}/pulls/comments/REPLY_COMMENT_ID --jq .body
GH_HOST=<derived-host> GH_REPO=OWNER/REPO gh api repos/{owner}/{repo}/pulls/comments/REPLY_COMMENT_ID --jq '.pull_request_review_id // empty'
```
第一个命令打印解码后的正文，其中必须显示真正的换行符。相反，如果它在一行内将 `\n`（或`\n\n`）显示为文字反斜杠-n 字符，则正文已转义：**不解析线程**。首先通过定界符重写正文来修复它，然后重新验证：
```bash
GH_HOST=<derived-host> GH_REPO=OWNER/REPO gh api --method PATCH repos/{owner}/{repo}/pulls/comments/REPLY_COMMENT_ID -f body="$(cat <<'EOF'
> the specific sentence being addressed from the reviewer's comment

Fixed in abc1234 — the lookup now null-checks before dereferencing.
EOF
)"
```
如果第二个命令打印评论 ID，则获取该评论并要求 `PENDING` 以外的状态；待处理状态意味着无论 POST 响应是否成功，回复都不会提交：
```bash
GH_HOST=<derived-host> GH_REPO=OWNER/REPO gh api repos/{owner}/{repo}/pulls/PR_NUMBER/reviews/REVIEW_ID --jq .state
```

3. **发布后重新获取待审核状态。**这会在初始获取后结束竞争并检测在回复循环期间创建的草稿：
```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/get-pr-comments" PR_NUMBER OWNER/REPO | jq -r '.pending_review // empty'
```
如果这打印了 ID，请停止而不解析此回复传递中的任何线程。报告待审核，但不要提交或丢弃它。

4. **使用 [scripts/resolve-pr-thread](../scripts/resolve-pr-thread) 解决**（如果缺少捆绑脚本，请使用 `gh api` 解决线程（如果支持）：
```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/resolve-pr-thread" THREAD_ID
```

### PR 评论和审核机构

这些无法通过GitHub的API解决。使用引用原始内容的顶级 PR 评论进行回复（传递 `-R OWNER/REPO` — 已解析的基础存储库 — 因此分叉→上游回复会发布在受监视的上游 PR 上，而不是分叉命名空间）：

```bash
REPLY_BODY_FILE="<absolute private OS scratch reply file>";
cat > "$REPLY_BODY_FILE" <<'EOF'
> the specific sentence being addressed from the reviewer's comment

Fixed in abc1234 — the lookup now null-checks before dereferencing.
EOF
GH_HOST=<derived-host> gh pr comment PR_NUMBER -R OWNER/REPO --body-file "$REPLY_BODY_FILE"
```

对于保存的回复，请使用其精确解码的字节填充文件，而不是运行说明性的此处文档。 `--body-file` 保留命令替换将删除的终端换行符。确认发布的正文与预期的 Markdown 匹配，包括实际的换行符。

在回复中包含足够的引用上下文，以便读者无需滚动即可了解正在处理的评论。

## 8. 核实

重新获取反馈以确认解决方案：

```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<derived-host> bash "$SKILL_DIR/scripts/get-pr-comments" PR_NUMBER OWNER/REPO
```

`review_threads` 数组应为空（`needs-human` 项除外）。

在恢复中，仅验证已保存的操作并通过其调用者结果报告新的反馈；返回[references/resume.md](resume.md)，不进入另一个修复周期。

**对于新鲜反馈模式，如果仍有新线程**，请检查迭代计数 - 计算轮数**针对此PR**，而不仅仅是此调用。像 `ce-babysit-pr` 这样的编排器每轮都会重新调用该技能，因此每次调用计数器永远不会触发；相反，计算分支上已经存在的早期审核修复提交（解决审核反馈的`git log <base>..HEAD`主题）加上本次运行自己的周期。

- **第一个或第二个修复验证周期**：对其余线程重复步骤 2。

- **第二个修复验证周期之后**（第三遍将开始）：停止循环。向用户显示剩余问题以及有关重复模式的上下文：“[area/theme] 的多轮反馈表明存在更深层次的问题。以下是我们迄今为止已修复的问题以及不断出现的问题。”使用相同的 `needs-human` 升级模式 - 保持线程打开并呈现模式供用户决定。

PR 评论和评审机构没有解析机制，因此它们仍然会出现在输出中。通过检查 PR 对话来验证他们是否得到回复。

## 9. Summary

在 `mode:return-to-caller` 中，在 [references/return-to-caller.md](return-to-caller.md) 中发出结构化结果，而不是下面的交互式摘要。返回之前保存实际的无更改完成和任何不完整的远程尾部；人类的决策保持开放并保留其类型化的有效负载。

简要总结所有已完成的工作。按结论分组，每项一行描述“做了什么”而不仅仅是“在哪里”。这是用户看到的主要输出，也是第 3 步（整合和决策）判断变得可见的地方：用户可以准确地看到修复了哪些内容、跳过了哪些内容以及原因。

格式：

```
已解决 PR #NUMBER 上的 M 个新项目中的 N 个：

已修复（计数）：[每个修复的简要说明]
以不同方式修复（计数）：[更改了什么以及方法不同的原因]
回复（计数）：[回答了哪些问题]
未解决（计数）：[跳过的内容和证据]
拒绝（计数）：[拒绝的内容以及引用的危害或范围原因；单独命名超出范围的项目，以便用户可以继续使用]

验证：[一行——例如，“bun 测试通过 (893/893)”或“bun 测试通过，但注意到 X 中预先存在的故障”；当没有提交代码更改时省略]
差异更改：[`git diff --shortstat` 从本次运行的第一次修复提交之前的头部到最后一次修复提交之后的头部，例如，“+42 / -7 across 3 files”；当没有提交代码更改时省略]
```

如果任何项目是 `needs-human`，请附加决策部分。这些情况很少见，但信号很高。每个都包含步骤 3 中组成的 `needs-human` 对象：引用的反馈、调查、自主操作不安全或不明确的原因、权衡的具体选项、建议（如果有），以及它所涵盖的每个仍然开放的线程的链接。

直接呈现 `decision_context` ——它已经被结构化以便用户快速决定：

```
## Needs your decision

1. [decision_context.quoted_feedback]
   - 已调查：[decision_context.调查]
   - 需要做出的决定：[decision_context.decision_reason]
   - 选项：[decision_context.选项，保留每个选项和权衡]
   - 推荐：[decision_context.推荐，当非空时]
   - 开放主题：[thread_urls]
```

`needs-human` 线程已经发布了听起来自然的确认回复，并且在 PR 上保持打开状态。

如果上一次运行有 **待决决定**（在步骤 2（分类）中检测到的线程已响应但仍未解决），请将它们列在新工作之后：

```
上次运行仍有待处理（计数）：

1. [主题path:line] -- [待处理内容的简要描述]
   先前回复：[链接到现有回复]
   [重新提出决策选项（如果有），或总结所询问的内容]
```

如果阻塞问题工具可用，请使用它来询问所有待处理的决策（新的 `needs-human` 和先前运行的待处理决策）。如果只有待决的决定并且没有完成新的工作，则摘要仅是待决的项目。

使用当前工具列表中已有的主机阻止问题工具（按功能匹配，而不是按主机特定名称匹配）。当前工具列表中的存在证明该工具存在；永远不要调用面向用户的提问工具来发现它是否存在。如果列出了匹配的工具但已卸载，请使用主机的工具发现机制来加载该功能 - 不要搜索其他主机的工具名称。用它来呈现决策并等待用户的响应。他们决定后，处理剩余的项目：修复代码、撰写回复、发布并解决线程。

仅当宿主中不存在阻塞工具或调用错误（例如，Codex编辑模式）时，才回退到在用户可见的摘要输出中呈现决策并在对话中等待，而不是因为需要模式加载。永远不要默默地跳过。如果用户没有响应，项目将在 PR 上保持打开状态以供稍后处理。
