# 确定审查的差异和范围

请在第 1 阶段阅读此内容。它定义了如何解析每个调用路径上的范围以及如何计算第 3 阶段（选择审查者）使用的确定性范围信号。

### 第一阶段：确定范围

计算差异范围、文件列表和差异。通过组合成尽可能少的命令来最小化权限提示。

**如果提供了 `base:` 参数（快速路径）：**

调用者已经知道 diff 基数。跳过所有基分支检测、远程解析和合并基计算。直接使用提供的值：

```
BASE_ARG="{base_arg}"
BASE=$(git merge-base HEAD "$BASE_ARG" 2>/dev/null) || BASE="$BASE_ARG"
```

然后产生与其他路径相同的输出：

```
echo "BASE:$BASE" && echo "FILES:" && git diff --name-only $BASE && echo "DIFF:" && git diff -U10 --irreversible-delete $BASE && echo "UNTRACKED:" && git ls-files --others --exclude-standard
```

该路径适用于任何引用 - SHA、`origin/main`、分支名称。当不需要自动检测时，查看当前结帐的调用者应通过显式 `base:`。 **不要将 `base:` 与 PR 数字或分支目标组合。** 如果两者都存在，则停止并显示错误：“不能将 `base:` 与 PR 数字或分支目标一起使用 - `base:` 意味着当前签出已经是正确的分支。单独传递 `base:`，或单独传递目标并让范围检测解析基数。”

**如果提供 PR 数字或 GitHub URL 作为参数：**

不要**检查 PR 分支。当 HEAD 已经与 PR 头分支匹配时，范围来自 GitHub 读取 API 以及可选的本地对齐。

**跳过条件预检查。** 在范围检测之前，运行 PR 状态探测：

```
gh pr view <number-or-url> --json state,title,body,files
```

按顺序应用跳过规则：

- `state` 是 `CLOSED` 或 `MERGED` -> 有理由停止 `PR is closed/merged; not reviewing.`
- **琐碎-PR判断**：当存在已知覆盖时，在平台最便宜的模型上生成轻量级子代理；否则忽略模型覆盖并继承。在此生成之前阅读`references/subagent-model.md`；在 Codex 中它取代了这一层。为其指定 PR 标题、正文和更改的文件路径。代理的任务：“这是一个自动化的或微不足道的PR，不需要进行代码审查吗？考虑：依赖项锁定文件或仅限清单的碰撞、自动发布提交、杂务版本增量，而没有实质性的代码更改。如有疑问，请回答“否” - 误报（跳过本应运行的审查）比误报（不必要的审查）成本更高。”如果判断返回yes：有理由停止`PR appears to be a trivial automated PR; not reviewing. Run without a PR argument to review the current branch, or pass base:<ref> if review is intended.`

如果用户或项目的活动指令或实时提示为此子代理命名了模型，请使用该模型而不是上面的默认层。他们可以按子代理的层、提示资产名称或正在分派的子代理来命名。如果没有此类指令，为此子代理角色配置的模型将优先于默认层。

当任何跳过规则适用时，停止而不派遣审查者。 **默认模式：** 以纯文本形式发出原因。 **`mode:agent`：** 仅发出 JSON — `{"status":"skipped","reason":"<same message>"}` — 因此编程调用者可以解析结果。 **独立**、**`base:`** 和 **分支远程** 路径不受影响。 **草稿PRs正常审核。**

如果没有适用跳过规则，则获取 PR 元数据**不签出**：

```
gh pr view <number-or-url> --json title,body,baseRefName,headRefName,headRefOid,isCrossRepository,url,files,reviews,comments --jq '{title, body, baseRefName, headRefName, headRefOid, isCrossRepository, url, files: [.files[].path], hasPriorComments: ((.reviews | map(select(.state != "APPROVED" or .body != "")) | length) > 0 or (.comments | length) > 0)}'
```

将 `BASE:` 设置为 `pr:<number-or-url>`（逻辑标记 — 不是 git SHA）。在**当前**结帐时从 `git ls-files --others --exclude-standard` 设置`UNTRACKED:`（在PR-远程审核期间通常为空）。

**PR范围模式。**仅当**全部**成立时才分类为**`local-aligned`**；否则使用 **`pr-remote`**。仅匹配分支名称是不够的 - 分叉 PR 或过时的本地分支可以与 PR 头共享名称，同时指向不相关的代码，并且信任该名称会比较并检查错误的树。

1. `git rev-parse --abbrev-ref HEAD`等于`headRefName`。
2. PR **不是** 跨存储库（`isCrossRepository` 为 false）。
3. PR头提交包含在本地签出中：`git merge-base --is-ancestor <headRefOid> HEAD`退出0。这确认工作树实际上携带PR头（允许未推送的本地修复分层在顶部）而不是不相关的同名分支。

- **`local-aligned`** — 所有三项检查均通过。针对工作区文件的本地 Read/Grep/git 责备对于 PR 已更改的路径有效。
- **`pr-remote`** — 任何检查都失败。工作树**不是** PR 头；已更改路径的工作区文件内容可能已过时或不相关。

**按范围模式进行差异**（不要混合远程和本地差异 - 矛盾的块会导致误报）：

- **`local-aligned`：** 从`baseRefName`解析`<resolved-base-ref>`（如果需要则获取）。计算`BASE=$(git merge-base HEAD <resolved-base-ref>)`，然后从`git diff --name-only $BASE`设置`FILES:`，从`git diff -U10 --irreversible-delete $BASE`设置`DIFF:`（包括PR分支上已提交、暂存和未暂存的更改）。 **不要**调用`gh pr diff`或附加远程块——当存在未推送的修复时，本地树是规范的。覆盖范围中的注释：`scope: local-aligned (PR; local tree diff)`。
- **`pr-remote`:** 从 PR `files` 数组中设置 `FILES:`。从`gh pr diff <number-or-url> --color=never`设置`DIFF:`。如果 `gh pr diff` 失败，请停止并显示可操作的错误 - 不要退回到结帐。然后从保存的输出中删除已删除的文件主体，就像 `--irreversible-delete` 在本地路径上所做的那样，使用`awk '/^diff --git /{del=0} del && !/^index /{next} /^deleted file mode /{del=1} {print}'`；切勿将`gh pr diff`直接插入过滤器，因为管道隐藏了其故障。

当 **`pr-remote`** 时，第 4 阶段之前：

1. 尽力获取 PR 头而不检出：`git fetch --no-tags origin <headRefName>:refs/review/pr-<number>-head`（替换元数据中的 PR 数字）。
2. 仅当 `git rev-parse refs/review/pr-<number>-head` 等于元数据 `headRefOid` 时，才为审查者和验证者设置 `PR_HEAD_REF=refs/review/pr-<number>-head`。成功的获取并不能证明 ref 是PR头：在跨存储库PR上，`origin`可以携带具有相同名称的不相关分支，并且PR可以在元数据调用和获取之间移动。当获取失败或 OID 不同时，省略 `PR_HEAD_REF` 并在覆盖范围中注明 — 审查者必须仅依赖 diff 块。
3. 尽最大努力获取 PR 基数而不检出：`git fetch --no-tags origin <baseRefName>`。成功后，使用 `git rev-parse FETCH_HEAD` 解析具体引用，并将 `PR_BASE_REF` 设置为该 SHA — 审查者和验证者用于文件级 git diff 的**真正的 git 基本引用**（例如 `data-migration-reviewer` 运行 `git diff <PR_BASE_REF> -- db/schema.rb`/`structure.sql`）。 `BASE:`中的`pr:<number-or-url>`逻辑标记仍然是范围标记； `PR_BASE_REF` 是可区分的基数。当获取失败时，省略 `PR_BASE_REF` 并在覆盖范围中注明 - schema-drift 和其他 git-diff 检查仅回退到 diff 块，并且不得**假设 `main`。
4. 将 `<pr-scope-mode>pr-remote</pr-scope-mode>` 以及设置后的 `<pr-head-ref>...</pr-head-ref>` 和 `<pr-base-ref>...</pr-base-ref>` 包含在第 4 阶段审核上下文包中。

**`pr-remote`** 模式下的审查者和阶段 5b 验证者不得** `FILES:` 中文件的Read/Grep 工作空间路径。设置 `PR_HEAD_REF` 时通过 `git show <PR_HEAD_REF>:<path>` 检查，否则仅使用提供的 diff 块。 **`local-aligned`** 使用正常的工作空间检查。

**如果提供分支名称作为参数：**

将提供的分支名称替换为 `<branch>`。 **不要**查看`<branch>`。

如果`git rev-parse --abbrev-ref HEAD`等于`<branch>`，则使用下面的**独立（当前分支）**路径——同一棵树，明确的分支名称；不要使用仅远程差异。

否则，比较 remote/local 参考 **无需结帐**：

1. 尝试 `gh pr view <branch> --json baseRefName,url,headRefName` — 如果 PR 存在，则更喜欢上面的 **PR number/URL 路径**（相同的远程 diff 规则）。
2. 否则，需要时在 `git fetch --no-tags origin <branch>` 之后将 `<branch>` 解析为 `origin/<branch>` 或 `<branch>`。
3. 解析默认基础分支（与独立逻辑相同）。计算 `BASE=$(git merge-base <base-ref> <branch-ref>)` 和 `git diff -U10 --irreversible-delete $BASE <branch-ref>`。
4. 如果`<branch-ref>`无法在本地解析，请停止：“无法在没有签出的情况下比较分支`<branch>`。签出该分支，传递其打开的PRURL/number，或使用`base:`查看当前分支。”

远程分支差异成功后，设置**分支远程范围**。工作树**不是** `<branch>`。将 `<pr-scope-mode>branch-remote</pr-scope-mode>` 和 `<branch-head-ref><branch-ref></branch-head-ref>` 包含在第 4 阶段审核上下文包中。审核者和阶段 5b 验证者不得** `FILES:` 中文件的Read/Grep 工作空间路径。仅通过 `git show <branch-ref>:<path>` 或 diff hunk 进行检查。

生产：

```
echo "BASE:$BASE" && echo "FILES:" && git diff --name-only $BASE <branch-ref> && echo "DIFF:" && git diff -U10 --irreversible-delete $BASE <branch-ref> && echo "UNTRACKED:" && git ls-files --others --exclude-standard
```

**如果没有参数（在当前分支上独立）：**

使用当前分支，应用与上述分支模式相同的基址检测逻辑（即，不带参数的 `gh pr view --json baseRefName,url` 默认为当前分支）。

如果无法解析任何碱基，**停止**。不要退回到`git diff HEAD`——没有基础的独立审查只会显示未提交的更改，并默默地错过分支上所有已提交的工作。

成功后，生成差异：

```
echo "BASE:$BASE" && echo "FILES:" && git diff --name-only $BASE && echo "DIFF:" && git diff -U10 --irreversible-delete $BASE && echo "UNTRACKED:" && git ls-files --others --exclude-standard
```

使用`git diff $BASE`（不使用`..HEAD`）将合并基础与工作树进行比较，其中包括已提交、暂存和未暂存的更改。

**整个文件删除不包含正文。** `--irreversible-delete` 保留每个已删除文件的 `deleted file mode` 标头和路径，并省略其旧内容，因此审查者不会读取更改删除的代码。需要删除主体的审查者从审阅库中读取它，如`references/diff-scope.md`所述。

**未跟踪的文件处理：** 始终检查 `UNTRACKED:`。除非上演，否则未跟踪的路径超出范围。当非空时，列出覆盖范围中排除的文件，并仅继续跟踪更改 - 从不停止或提示。

### 第 1b 阶段：计算示波器信号（廉价、确定性）

使用 `scripts/review-scope.py` 从该技能的目录中导出一次确定性事实。帮助程序验证端点、计算更改的线路、派生路径类并报告楼层。它从不奖励精简版。不要在散文中重现这些机制或从差异块中估计它们。下面的调用是助手的契约：直接运行它，而不是检查脚本或探测其 `--help`，除非它实际上因不兼容而失败。

将 `SCOPE_MODE` 设置为 Stage 1 作用域模式，并将 `DIFF_A`/`DIFF_B` 设置为其两个端点：
- **`local-aligned`/独立/`base:`** - `DIFF_A="$BASE"`（真正的SHA/ref），`DIFF_B`空（比较基础树与工作树）。
- **`pr-remote` / `branch-remote`** — `DIFF_A=<PR_BASE_REF>`、`DIFF_B=<PR_HEAD_REF>`（或`<branch-head-ref>`）— 从第 1 阶段获取的引用。

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
if [ "$SCOPE_MODE" = "pr-remote" ] || [ "$SCOPE_MODE" = "branch-remote" ]; then
  "$PY" "$SKILL_DIR/scripts/review-scope.py" --base "${DIFF_A:-}" --head "${DIFF_B:-}" --docs-root "<root>";
else
  "$PY" "$SKILL_DIR/scripts/review-scope.py" --base "$DIFF_A" --docs-root "<root>";
fi
```

远程作用域始终传递两个端点标志，即使尽力获取将一个值留空时也是如此；然后，助手拒绝计算，而不是将获取的基数与不相关的本地工作树进行比较。 加载 JSON 结果。 `hard_block_full`是`references/modes-and-output.md`复习深度门的楼层；它涵盖了指定的硬块类、未计数的文件以及`size_band`或`large`（整个楼层的可执行非测试更改行）。 `silent_pass_classes` 指定守卫在该门下进行后果评估，而不是在深度楼层。 两者都没有简单的奖励，并且低于地板的计数本身并不能决定任何事情。 整个文件删除不在上面的任何行计数中：帮助程序将它们列在 `deleted_files` 中，在 `deleted_exec_nontest_lines` 中对它们的可执行非测试行进行计数，以及在门读取的 `deleted_band`（`none`、`small` 或 `large`）中计数的带区。 `signals` 是路径启发法，不是选择决策，也不是精简版块。 在此阶段之后，在阅读任何后续引用文档之前应用该门。 总体而言，第 3 阶段仍然判断基于内容的风险，例如身份验证、支付、突变、外部I/O、并发性和流程执行。 使用 `test_files_changed`、`agent_surface`、`has_learnings_corpus` 和 `declared_packs` 作为选择通用审查者的条件的输入，而不是作为自动生成决策。 `declared_packs`报告本地CE配置是否命名任何Compound Pack，仅从配置中读取（没有解析任何内容，因此`pack_roots`始终为0）； `references/persona-catalog.md` 中的学习选择规则决定该事实在整个脊柱上选择什么，`references/depth-paths.md` 决定精简路径和集中路径如何使用它。 它描述了本地签出，因此帮助程序仅在本地范围内对其进行评估：在远程范围中，它是 `null` 并且没有解析器运行。 在局部范围内，`null`表示助手无法分辨；自己阅读配置的 `packs:` 键。

### 阶段 1c：将条件文件映射到更改的路径

**目标：** 将管理此更改的每个标准文件与其管理的已更改文件配对的映射。路径，而不是内容。两个深度路径都会消耗它：精简路径在上下文中检查它的差异，并且阶段 3b 决定从中调度 `project-standards`。

从**正在审查的树**中枚举候选者，而不是从碰巧检出的任何一棵树中枚举候选者：仅在`local-aligned`范围内的工作区，以及在`pr-remote`和`branch-remote`中审查的头引用（第1阶段解决了哪个）。必须出现仅存在于所审阅的树中的标准文件，并且不能出现在那里删除的标准文件，否则审阅会强制执行更改从未有过的标准。

候选者是任意深度的 `CODING_STANDARDS.md`、`CLAUDE.md` 和 `AGENTS.md`。保留那些目录是已更改文件的祖先的目录 - 根级文件控制整个签出，`skills/AGENTS.md`仅控制`skills/`下的内容。

`CODING_STANDARDS.md` 是指定的标准源，因此指令文件仅为不受`CODING_STANDARDS.md` 管辖的已更改文件提供标准，并且不会针对这两种类型对文件进行评分。每个管理`CODING_STANDARDS.md`累积适用。当其中两个规定的规则不能同时适用于同一已更改的文件时，由较接近该文件的目录的规则决定，因此嵌套文件的规则仅适用于其目录下已更改的文件。声明的Compound Pack不是这里的标准类型。在整个书脊上，他们选择`learnings-researcher`，这对他们进行评分；在精简和集中的路径上，它们根据上下文进行分级。无论哪种方式，它们都是与标准文件分开分级的，因此违反标准规则和包规则的行会为每个源产生一个结果。

**完成** 当没有可以根据两种标准对更改的文件进行评分时。没有标准文件控制的更改文件是完整的结果，而不是间隙。搜索失败或不确定范围会被准确记录，而不是空结果；审查深度门和阶段 3b 各自说明了其对他们的意义。

立即创建审核运行目录。每条路径，无论是精简路径还是完整路径，都会在那里写入其产物：

```bash
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
RUN_ID=$(date +%Y%m%d-%H%M%S)-$(head -c4 /dev/urandom | od -An -tx1 | tr -d ' ');
RUN_DIR="$SCRATCH_ROOT/ce-code-review/$RUN_ID";
(umask 077; mkdir -p "$RUN_DIR") || exit 1; chmod 700 "$RUN_DIR" || exit 1;
echo "$RUN_DIR";
```

### 阶段日志

每次运行都会记录每个阶段的成本，因此可以根据测量的运行来设置该技能使用的阈值。记录为`<run-dir>/stages.jsonl`，仅由下面的捆绑脚本编写；收据编写器将其折叠到末尾的`metadata.json`（`summarize`，在每个路径写入其收据的位置命名）。现在，在打印运行目录的同一个 shell 调用中打开范围阶段，您可以：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/run-log.py" event --run-dir "$RUN_DIR" --start scope
```

之后的每个边界都是一次调用中的 `--end <stage> --start <stage>` 相同的调用，以及 `--reviewers`、`--candidates`、`--tokens`（仅当主机向您提供计数时）或 `--fact key=value` 来了解该阶段学到的内容。舞台名称是固定的：`scope`，然后是 lite 和 focus 上的 `review` 和 `receipt`（焦点上 `peer` 与 `review` 重叠），或者整个书脊上的 `select`、`dispatch`、`validate`、`merge` 和 `report` （`peer` 与 `dispatch` 重叠）。将调用折叠到该步骤已在任何地方存在的 shell 调用中；边界永远不会轮到自己。

### 第 1d 阶段：制定审查政策

**目标：** 存储库的审核策略，从副本中读取正在审核的更改无法编辑的内容，并暂存到每个后来的读者都可以找到它的地方。

审核策略是一个 `REVIEW.md` 文件：说明审核在此存储库中的行为方式，例如这里每个严重性的含义、要跳过的查找路径或类别、次要发现的上限、查找需求类别的证据，或对每次更改运行的检查。 Claude Code 审阅读取同一文件。它不是标准文件：它既不提供标准也不取代它们，因此 Stage 1c 的优先级会忽略它。

- **哪些文件。** 根`REVIEW.md` 控制整个更改。作为已更改文件的祖先的目录中的 `REVIEW.md` 将添加到其下路径的根文件中。
- **哪个副本。** 从第 1 阶段基础（`BASE:` 或 `pr-remote` 中的 `PR_BASE_REF`）读取每个文件，而不是从已审核的树中读取，因为不得根据其自己编写的策略来审核更改。当 diff 添加、编辑或删除策略文件时，将应用基本副本（对于新文件则不适用），并且 Coverage 表示未应用更改的版本。
- **包括。** 在根文件中，仅包含 `@<path>` 的行代表该文件，从同一引用读取，深一层。跳过此审核已读取为标准的文件的包含，例如 `@CODING_STANDARDS.md`。

将您读到的内容写入`<run-dir>/review-policy.md`，每个文件都有一个标题，该标题指定了其路径及其管理的路径。基础上没有策略文件是完整的结果：什么也不写。您找到但无法读取的策略文件会在 Coverage 中记录为未读，而不会被视为不存在。

## 任务可见性

对于多代理路径，一旦解决了审查范围，就可以使用平台的任务跟踪功能（如果可用）来显示从执行脊柱派生的面向用户的简短视图。跟踪审核结果，而不是个人角色、设置机制或工具调用；仅在满足条件时添加条件工作，并在有意义的转换时更新视图。如果没有可用的任务跟踪功能，请继续正常进度和最终报告，而无需在聊天中模拟任务列表。
