# `gh stack` 该技能依赖的语义

已验证`gh stack version 0.1.0`。 `gh stack <command> --help` 具有权威性 — 如果它与此处的任何内容不同意，请遵循 `--help` 并在报告中说明。 （`gh stack help <command>` 不起作用；它打印顶级帮助。）

仅列出在堆栈模式下更改决策的行为。该文件是独立的
目的：不依赖于用户安装了单独的`gh-stack`技能。

## 对父级进行分类

```bash
gh stack checkout "<parent-pr-number>"
```

只要存在一个父级，就通过 **PR 数字** 解析父级 - 这就是从 GitHub 下拉堆栈的原因。裸分支名称仅针对**本地**堆栈进行解析，因此仅分支父级可以在本地进行分类，而无需进一步分类。

退出代码上的分支；状态文本将发送到 stderr 并且不能被解析。

| 出口 | 意义 | 这里的意思是什么 |
|---|---|---|
| 0 | 成功 | 父级在堆栈中，并且 `HEAD` 已移至其中 |
| 2 | 不在堆栈中 | 父级是独立的；没有检查或获取任何内容 |
| 5 | 无效参数 | 修复调用；见`--help` |
| 6 | 需要消除歧义 | 分支位于多个堆栈中 — 检查非共享分支 |
| 9 | 堆叠PRs不可用 | 在此存储库上未启用；告诉用户并停止 |

```bash
gh stack view --json    # JSON on stdout: trunk, currentBranch,
                        # branches[] { name, head, base, isCurrent, isMerged, needsRebase,
                        #              pr { number, url, state } }
```

`base` 是分支最后已知包含的父 SHA，而不是父当前的提示；当该尖端不再是祖先时，`needsRebase`为真。没有命名堆栈顶部的字段，也没有记录的分支顺序，因此不要从此有效负载派生位置 - 使用 `add` 的出口 5 代替。

## 解决PR头

`gh pr view "<n>" --json headRefName,headRefOid,author` 识别头部； `headRefName` 单独不会，因为相同的存储库名称可能在本地不存在或过时，并且可能与不相关的分支发生冲突。在 `headRefOid` 创建本地分支，当该提交无法访问时获取 `refs/pull/<n>/head` — 可访问性使该提交没有可命名的分支。

## 建筑

```bash
gh stack init [--base "<trunk>"] "<branch>"...
```

从下到上处理分支并检查**最后**一个。 **采用现有分支机构；创建丢失的**——第一个来自主干，后面的每个来自它之前的分支。没有单独的采用模式：存在决定。 `--base` 选择非默认主干，因此父分支可以作为主干而无需加入堆栈。

```bash
gh stack add "<branch>"
```

必须从堆栈的 **top** 分支运行（或在主干仍为空时）；其他任何地方都有 **5** 出口。这里的 Exit 5 意味着“你不在顶部”，用 `gh stack top` 移动到那里是一个决定，而不是修复：它改变了新分支的父级。这是否正确取决于调用者——当指定一个特定的父对象时，情况就不是这样了。如果没有 `-Am`，`add` 不会触及工作树，因此暂存和未暂存的更改会跟随到新分支上。

```bash
gh stack submit --auto [--open]
```

`--auto` 避免了每个新PR 出现标题提示。 `--open` 创建可供审核的PRs（而不是草稿），并且还将预先存在的草稿标记为就绪。

## 绝不

- **`gh stack link`** — GitHub - 仅根据设计，不创建本地跟踪，因此稍后的 `gh stack submit`、`gh stack view` 或 `gh stack merge` 将看不到该图层。它适用于由外部工具（jj、Sapling、git-town）管理的分支。
- **`gh pr merge`** 在堆栈成员上 - 它无法合并堆栈。着陆使用`gh stack merge`。
- **裸 `view` / `submit` / `init` / `add` / `checkout`** — 每个都会提示或打开在 PTY 下阻塞的 TUI。始终传递上面显示的参数和标志。
