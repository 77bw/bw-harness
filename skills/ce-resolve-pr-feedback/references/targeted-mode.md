# 针对性模式

当模式检测（在 SKILL.md 中）路由到 **目标模式** 时，请阅读此参考 - 提供了特定的评论或线程 URL。目标模式仅针对该线程。

## 1. 提取线程上下文

解析 URL 以提取 HOST、OWNER、REPO、PR 编号和评论 REST ID：
```
https://HOST/OWNER/REPO/pull/NUMBER#discussion_rCOMMENT_ID
```

**GitHub 企业主机。** 从 URL 中获取主机（目标模式始终是 URL 触发的）。当它不是** `github.com` 时，将其作为 `GH_HOST=<host>` env 前缀内联传递到下面的 **每个** `gh api` / 捆绑脚本调用上（`gh api` 尊重 `GH_HOST` 作为请求主机），以便在正确的主机而不是 `github.com` 上获取、回复和解析企业线程。在 `github.com` 上，删除 `GH_HOST=<host> ` 前缀。将同一主机带入您从完整模式步骤 5-7 运行的 reply/resolve 调用。

**第 1 步** -- 通过 REST 获取评论详细信息和 GraphQL 节点 ID（便宜，单个评论）：
```bash
GH_HOST=<host> gh api repos/OWNER/REPO/pulls/comments/COMMENT_ID \
  --jq '{node_id, path, line, body}'   # omit GH_HOST=<host> on github.com
```

**第 2 步** -- 将评论映射到其线程 ID。使用[scripts/get-thread-for-comment](../scripts/get-thread-for-comment)。将 `SKILL_DIR` 设置为您加载 ce-resolve-pr-feedback SKILL.md 的绝对目录 — Bash 工具的 CWD 是用户的项目，而不是技能目录，并且 shell 状态在 Bash 调用之间不会保留，因此将其设置为内联。如果捆绑的脚本丢失，请使用完整模式的回退 `gh` 命令来检查 PR 注释：
```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
GH_HOST=<host> bash "$SKILL_DIR/scripts/get-thread-for-comment" PR_NUMBER COMMENT_NODE_ID [OWNER/REPO]
```

这会获取线程 ID 及其第一个评论 ID（最小字段，无正文），并返回包含完整评论详细信息的匹配线程。

**第 3 步**——在进行任何工作之前检查您自己未提交的审核。当您持有回复时发布的回复将被吸收到该草稿中：调用会返回评论 ID 和 URL，就好像成功一样，但审查者在草稿提交之前看不到任何内容。完整模式从`get-pr-comments`免费获得此功能；目标模式永远不会调用该脚本，因此请直接检查（待处理的评论仅对其作者可见，因此任何点击都是您的）：
```bash
GH_HOST=<host> gh api --paginate repos/OWNER/REPO/pulls/PR_NUMBER/reviews --jq '.[] | select(.state == "PENDING") | .id'
```
`--paginate` 是必需的：此端点按时间顺序排列，页数为 30，因此草稿可以对过去的第 1 页进行排序。打印 ID 而不是计数 — `--jq` 每页运行，因此计数每页发出一个数字，但 ID 只是连接起来并在没有草稿时保持为空。 （`--slurp`不是一个选项；`gh`与`--jq`一起拒绝它。）

如果打印出任何内容，请停止。告诉用户他们对 PR 有未提交的评论，并且必须先提交或放弃该评论，然后此技能才能回复。请勿自行提交或丢弃；审查草案是未发送的人类写作。

## 2. 判断、修复、回复、解决

应用完整模式第7步（回复和解决）判断前的完成检查：分别检查线程是否已经有可见的提交回复以及是否已经解决。当线程已经`resolution-pending`时，第7步定义了唯一剩下的工作：跳过判断、修复、验证和提交，然后完成缺少的解决方案而无需再次发布。

**首先判断。** 在您自己的上下文中，将 `references/evaluation-rubric.md` 中的标题应用于此线程。考虑 `isOutdated` 和位置字段（`line`、`originalLine`、`startLine`、`originalStartLine`）——目标线程也可能已过时，需要相同的重定位处理。该标题的跨项目推理对单个线程没有任何作用，但其阅读深度和转移规则完全适用（判断之前阅读的深度，以及何时停止回复、拒绝或人为决定而不是修复）：在接受有争议的发现或看似故意的重写代码之前进行深度阅读（调用者、不变量、`git blame`/PR作者意图的基本原理）。这个判断决定了调查结果是否有效；不要只关注审稿人的权威。

**然后根据判决采取行动：**

- **`fixed` / `fixed-differently`** — 阅读 `references/agents/pr-comment-resolver.md` 并在此上下文中自行应用修复程序，使用该提示作为您自己的指令并生成其返回记录（`files_changed`、`reply_text`），共享验证、提交和回复步骤将使用该记录。您已经阅读了代码来判断它，并且单个修复程序无法并行运行。仅当修复远远超出您判断所读取的代码（跨调用者的重命名、对许多站点的类修复）时，才调度带有该修复程序提示的单个通用子代理。不要在 type/name 之前派遣独立代理。向其传递 file/location 字段（已解析的位置或锚点，如果已过时）、注释文本以及有关要更改的内容及其有效原因的注释。修复程序仅实现；它不会重新判断。当该调度不可用或失败时，请在此处应用修复（请参阅完整模式步骤 4，修复）。
- **`replied` / `not-addressing` / `declined`** — 无子代理。根据标题撰写回复文本，然后继续reply/resolve。
- **`needs-human`** — 撰写`decision_context`，运行标题的“升级前裁决”步骤（有判断力的项目可能会作为上述判决之一返回），剩下的内容根据标题撰写听起来自然的回复，保持线程打开（不解决），并向用户呈现决定（使用平台的阻塞问题工具，如完整模式步骤 9 中所示）。下面的共享回复步骤将回复发布一次 - 不要在此处发布。

然后在所选执行模式下执行完整模式步骤 5-7（`references/full-mode.md`）。普通和管道运行验证、提交、发布和完成对话。返回调用者验证并提交代码修复，保存该线程的完成操作，然后返回而不进行推送或远程完成写入。当没有代码改变时，跳过validate/commit，使用现有的reply/resolve协议，然后通过`references/return-to-caller.md`保存其实际完成或未完成的进度。其结构化结果取代了交互式决策问题。
