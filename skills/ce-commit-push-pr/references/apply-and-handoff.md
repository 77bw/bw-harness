# 应用 PR、报告和PR 看护交接

**仅描述模式** — 打印标题和正文。除非用户要求申请，否则停止。

**新PR**（完整工作流程，步骤 1 中没有现有的PR，解析分支和PR状态）—如果**堆栈模式**处于活动状态，请按照`references/stack-submit.md`而不是`gh pr create`的提交部分进行操作；然后报告底部打开的非草稿PR URL并继续PR 看护交接。否则，在创建之前，**总是**重新运行 `gh pr list --head <branch> --state open --json number,url,isDraft,headRefName,headRepositoryOwner` （仅分支名称；针对每个上下文的分叉上的基本存储库）。这会捕获自第 1 步以来出现的 PR，或者第 1 步检查中由于返回**未知**而错过的一个，因此您不会打开重复项。如果列表现在显示一个 PR，其 `headRepositoryOwner` 和 `headRefName` 与当前头匹配，则切换到现有的-PR 路径。当多个分叉匹配时，按照步骤 1 中的方式按头所有者进行选择，而不是假设索引为 0。如果此重新检查本身退出非零，则在创建之前解析 `gh auth status` 或连接；不要假设 PR 不存在。否则，请使用`gh pr create`按照下面的“通过 gh 申请”进行申请。仅当用户或项目需要时将其作为草稿打开；此运行无法进行验证，属于正文，不处于草稿状态。报告网址。

**现有PR**（完整工作流程，在步骤1中找到）-如果**堆栈模式**处于活动状态，仍然遵循`references/stack-submit.md`的提交部分，以便其余堆栈层提交或同步（从堆栈中间传送是正常的）；然后报告底部打开的非草稿PR URL，并继续以下面导出的姿势进行PR 看护切换。否则，新提交已经位于步骤 3 中的 PR 上（提交和推送）。报告PR URL，然后询问是否重写描述。

- **否** — 跳过描述重写并继续下面的PR 看护交接规则。
- **是** — 如果尚未完成，请运行步骤 4（组成 PR 标题和正文），然后预览并应用（见下文）。

**描述更新模式，或现有-PR重写确认** — 应用前预览。首先将提议的标题和正文与现有的PR进行比较。如果相同，则保留现有的标题和正文，并且不调用`gh pr edit`。如果唯一的区别是仅品牌的增量，并且用户没有明确请求确切的品牌更改，则还保留现有的标题和正文；品牌本身永远不会产生应用意图。否则询问：“新标题：`<title>`（`<N>`字符）。摘要开头为：`<first two sentences>`。正文：`<L>`行。申请吗？”如果拒绝，用户可以将焦点文本传回以重新生成；不适用。如果确认，请按照下面的“通过 gh 申请”使用 `gh pr edit` 进行申请并报告 URL。

**解释器归档** - 仅在完整工作流程中运行，当所有这些都满足时：`pr_teaching_archive`打开，组合体具有`## New concepts`部分，并且应用已确认（新的-PR创建，或现有的-PR重写用户接受）。拒绝重写会完全跳过存档，因此不会留下未链接的文档提交。解析来自 Context 中收集的存储库根的每一条路径，而不是来自 CWD 的路径。通过两个教授的概念，为每个概念编写一个文件，并在一次提交中进行阶段。首先解决`<root>`：

<!-- ce-docs-root:start -->
**在组成任何产物路径之前解析 CE 产物根 `<root>`。**

- **仅从 `<repo-root>/.compound-engineering/config.yaml` 读取** `docs_root` (`<repo-root>` = `git rev-parse --show-toplevel`)。不要从`config.local.yaml`开始阅读。取消设置 -> `<root>` 为 `docs`，与之前完全相同。
- **验证**设置值：一个存储库相对目录，其真实的符号链接解析路径保留在存储库内，既不是存储库根目录，也不是位于 `.git/` 下。否则，会因命名 `docs_root` 和值时出错而停止 - 永远不会回退到 `docs`。
- **使用** `<root>` 作为唯一的产物位置：如果不存在则创建它，将每个路径与该技能自己的子目录组成 `<root>/<subdir>`，并且永远不要读取 `docs`。
<!-- ce-docs-root:end -->

然后在 `gh` 调用之前按顺序运行这些步骤：

1. `git check-ignore -q <root>/explainers/YYYY-MM-DD-<concept-slug>.md`（来自存储库根）——检查适用于尚不存在的路径。如果路径被忽略，则打印一行警告并完全跳过归档，不写入任何内容（从不`git add -f`）。
2. 将YAML frontmatter `title`、`date`、`input_shape: concept`、`subject`以及教学内容写入文件（需要时创建目录）。如果该文件在之前的运行中已存在，则覆盖它。
3. 仅`git add`那些文件（从不`-A`）并使用`docs(explainer): teach <concept>[, <concept>]`提交。将**项目发布门**重新应用到生成的提交状态，然后推送。如果提交报告没有任何要提交的内容，则该文档已经从之前的运行中提交 - 保留链接并继续。
4. 在应用之前，将每个文档的头分支 blob URL 添加到 `## New concepts` 部分。构建存储库实际主机的 URL — 例如，`gh browse -n -b <head-branch> -- <path>` 在任何主机 `gh` 目标（包括 GitHub Enterprise）上打印链接。不要对 `github.com` 或 GHE 上的链接 404 进行硬编码。

如果文档写入、提交或推送失败，则发出警告并继续创建PR，无需链接。切勿让提交和 PR 之间的流程停止。

**用户可运行的调用渲染。** 对于下面的输出切换，默认为 `/ce-explain <name>`。仅当活动主机为 Codex 或明确记录以美元为前缀的技能调用时，才使用 `$ce-explain <name>`。仅将调用呈现为内联代码并仅输出一种形式。

**概念预告片** — 当此运行应用的主体包含 `## New concepts` 部分时，在每种模式下在 PR URL 后打印一行：`New concepts: <name>[, <name>]`。在交互式完整工作流程运行中，每个教授的概念用一行来告诉用户使用上面的渲染规则调用`ce-explain <name>`。当此运行未应用正文时（包括被拒绝的重写或管道模式默认为否）或不存在 PR 时，不打印预告片。

**在应用下面的移交规则之前解决常设选择退出问题。** 在移交时按照此处的规则阅读`auto_babysit`。从先前步骤读取的配置不会延续：在没有读取密钥的情况下到达切换的运行会根据用户的站立选择进行切换，并且压缩运行是发生的常见方式。

<!-- ce-config-layers:start -->
**解析两个存储库文件中的普通 CE yaml 密钥。**

- **读取** `<repo-root>/.compound-engineering/config.local.yaml`，然后读取 `config.yaml` (`<repo-root>` = `git rev-parse --show-toplevel`)。丢失的文件将被跳过。 Gitignore 不会改变分辨率。
- **以第一个活动（未注释）值获胜**。对于标量，未设置空；无效值继续下一层，则技能默认。对于列表和地图，现有的键（包括空列表或地图）将替换整个键。
- **不要**将此规则用于 `docs_root` — 该键仅是 `config.yaml`。
<!-- ce-config-layers:end -->

仅当获胜活跃值恰好为 `false` 时，Babysit 才会关闭；缺少的键或任何其他值都会保留默认**打开**。用户选择退出的交接是**此运行的成功终端**，而不是被阻止的终端 - 报告 PR URL，在一行中说婴儿看护被站立配置跳过，然后停止。

**PR 看护切换 — 默认开启；完成门。** 在新创建的 PR、成功的堆栈提交或现有打开的 PR 上的新提交之后，直到 `ce-babysit-pr` 拥有后续操作或应用下面的显式跳过时，才会完成此运行。仅报告 PR URL 并不成功。在一条无阻塞线路中宣布自动切换，然后通过主机正常的技能调用机制调用技能；永远不要问yes/no。对 PR 链接的请求、返回报告或不合并都不是跳过：`ce-babysit-pr` 永远不会合并，除非要求登陆堆栈。

堆栈提交后，当用户明确要求登陆时，将底部打开的非草稿 PR 与派生的 `posture:stack-ready` 或 `posture:stack-land` 一起移交，以及当管道提交堆栈时的堆栈范围范围。报告所有权转移，以便外部协调器不会在当前分支上启动第二个裸照管者。

**成功** = `ce-babysit-pr` 拥有监控生命周期。在选择监控模式之前加载并遵循其说明。如果您在此会话中运行它，请继续，直到其停止条件允许最终报告，仅当其武装唤醒源将该代理带回来时才结束转弯。在`mode:pipeline`中，等待其管道停止并返回结构化结果。在报告成功之前，在 `## Needs your decision` 下渲染每个返回的类型化 `needs-human` 残差不变，并将相同的对象传递给顶级协调器。 `babysit:off` 仅禁用新监控；它不会抑制本次运行已知的或由其调用者提供的类型残差。

在`mode:pipeline`中，该技能写入的最后一件事是返回给调用者。它结束了该技能，而不是回合。调用者在同一个会话中运行，返回后执行下一步。该返回是本次运行等待`ce-babysit-pr`后的结构化结果，或者是切换未触发时已写入的报告。

切勿自己启动PR 看护机制：不要运行 `pr-snapshot`、武装观察者或重建循环。切勿单独替换`ci-watcher`、`gh pr checks --watch`、主持人自己的PR观看工具、临时民意调查或稍后照顾的承诺。 `ce-babysit-pr` 决定如何唤醒，包括当主机指令指示 PR 等待时通过主机工具唤醒。 **切换被阻止：**如果技能无法加载或启动，则停止并报告故障。不要发明平行或更窄的手表。

无论配置如何规定，此调用上的 `babysit:` 令牌决定此运行 - `off` 跳过，`continuous` 和 `checkpoint` 强制该模式并即使在长期选择退出的情况下运行。如果没有这样的令牌，则由上面解析的`auto_babysit`决定。

当PR 看护开启时，仅草稿堆栈提交是PR 看护之前的硬残留。

**不触发（自动检测，无需标记）：**在任何这些情况下都不会启动自动切换。
- `mode:pipeline` **除了**当此运行完成堆栈模式提交时（然后按照上面的派生姿势进行切换）。
- 仅描述或描述更新模式。
- 没有 PR 创建或更新此运行。
- 非GitHub主机。
- 本次运行创建或更新了 **草稿 PR**。草稿是作者未准备好的信号：宣布跳过，并说一旦PR准备好就可以开始`ce-babysit-pr`。显式的 `babysit:continuous` 或 `babysit:checkpoint` 仍然会强制监视 — 将 `watch` 或 `checkpoint` 传递到调用中，以便其草拟边界臂。
- **您无法推送到的头部分支。** **当您可以推送头部时，分叉 PRs 是可驱动的 - 不是硬性**（对于此技能刚刚推送的分支来说很常见）：babysit 读取 **base** 存储库上的状态并将修复推送到 **head** 存储库。仅当头部不可推动时才硬关闭。
**软降级（仅在成功切换后）：** `ce-babysit-pr` 决定是否应用检查点模式并拥有其报告和恢复调用。检查点并不能替代失败的切换。

## 通过gh申请

正文**必须**写入临时文件并通过 `--body-file <path>` 传递。切勿使用 `--body-file -`、stdin 管道、heredoc-to-stdin 或 `--body "$(cat ...)"` — 包装器和 stdin 处理可以默默地生成一个空的 PR 主体，而 `gh` 仍然退出 0 并返回 URL。

```bash
BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/ce-pr-body.XXXXXX") && cat >> "$BODY_FILE" <<'__CE_PR_BODY_END__'
<the composed body markdown goes here, verbatim>
__CE_PR_BODY_END__
```

带引号的哨兵可以防止 `$VAR`、反引号和正文中的任何文字 `EOF` 被扩展。

对于`<TITLE>`：逐字替换。如果它包含 `"`, `` ` ``, `$`, or `\`，转义它们或切换到单引号。

```bash
gh pr create --title "<TITLE>" --body-file "$BODY_FILE"   # new PR
gh pr edit   --title "<TITLE>" --body-file "$BODY_FILE"   # existing PR
```

**屏幕截图。** 当正文引用 `references/visual-evidence.md` 中的本地图像时，在图像目录中创建正文文件，以便每个 `./<name>.png` 引用解析为：`BODY_FILE=$(mktemp "<images-dir>/ce-pr-body.XXXXXX")`。在创建或编辑命令中为每个图像添加一个 `--attach "<images-dir>/<name>.png#<alt text>"`。 `gh` 上传每个文件并将匹配的引用重写到其 GitHub URL。

文件`gh`在上传前被拒绝，例如丢失文件或超过10 MB的图像，使其以非零值退出，而无需创建或编辑PR； stderr 命名该文件。在其他人成功后失败的上传仍然可以保留创建或更新的PR，并且`gh`仍然打印其URL。因此，无论退出状态如何，都不要再次运行 `gh pr create`。从打印的 URL 中找到 PR，或者按照上面 new-PR 在没有打印任何内容时重新检查的方式，并使用 `gh pr view "<pr-url>" --json body` 读取其正文。如果那里的任何图像引用仍然指向本地路径，请编辑 GitHub 上的 PR 主体以删除这些引用并保留其他所有内容。如果创建或编辑不适用，请再次应用正文，不包含失败的图像。无论哪种方式，请报告哪些图像未上传。
