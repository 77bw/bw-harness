# 托管堆栈CLI配方

当活动运行使用已确认的托管堆栈 (`manager_status == "confirmed"`) 并需要 `gh stack` 命令配方时加载此文件。软依赖于 CLI：如果 `gh stack` 丢失或退出不可用（例如代码 9），则显示清晰的残余 - 不要从拓扑中发明托管成员资格。

始终是非交互的。更喜欢 JSON/view 探针和显式分支名称；永远不要依赖交互式提示。将 `<tracking-remote>` 替换为堆栈分支的实际跟踪远程（通常是 `origin`，但也可能是 `upstream` 或分支远程）——当 SKILL.md 已经解析了不同的跟踪远程时，切勿硬编码 `origin`。

## 在活动层上进行自有推送后（存在依赖项）

```bash
gh stack rebase "<first-open-dependent-branch>" --upstack --no-trunk --remote <tracking-remote>
gh stack push --remote <tracking-remote>
```

从第一个依赖项开始，将活动目标从级联变基中排除。引用分支名称 — git 分支名称可能包含 shell 元字符。冲突时：`gh stack rebase --abort`，然后显示需求人类/堆栈同步残差。

## 在新鲜结账时检查一层

```bash
gh stack checkout <PR_NUMBER>
```

使用 PR 数字，从 GitHub 中提取堆栈。分支名称仅解析本地已知的堆栈，并且 `gh pr checkout` 让管理器不知道分支。

## 发现订单/下一个开放层

```bash
gh stack view --json
```

## 登陆一个前缀（仅限`posture:stack-land`以下）

合并 **最底部打开的已解决** PR — `gh stack merge <PR>` 通过 PR 原子地合并完整堆栈前缀。当打算单前缀着陆时，切勿合并上栈活动PR，而下栈PRs保持打开状态。

```bash
gh stack merge <BOTTOM_MOST_OPEN_SETTLED_PR> --yes --squash
gh stack sync --remote <tracking-remote>
```

仅在合并成功后运行同步。合并失败后的同步会变基并推送每一层，从而重新启动其 CI 和审查。如果合并表明另一个进程正在编辑堆栈，请立即重试：该锁定是临时的，并且一个克隆的所有工作树共享它。

在前进之前重新探测已落地的PR：在合并队列基础上，CLI可能会在入队后成功，而PR保持打开状态——继续观察或返回排队的残差，直到`pr_state`为`MERGED`。只有这样才能将刚刚合并的PR视为**层过渡**（停止观察器，重新探测，继续下一个需要重新声明姿势的打开的非草稿）——而不是此PR 看护调用的运行级终端停止。

## 禁止在托管堆栈成员上使用

```bash
gh pr merge …
```

仅使用 `gh stack merge`。在`posture:target`和`posture:stack-ready`下，在报告ready-as-next时打印确切的合并命令；不要执行它。
