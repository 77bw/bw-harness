# 从默认分支创建分支

本地`<base>`可能有过时的提交（另一个session/worktree推进了它）或提交了打算从以后分支的用户。本地 git 无法区分这些 - 询问何时存在未推送的提交。

## 决策流程

### 1. 获取新的远程基地

```bash
git fetch --no-tags origin <base>
```

如果获取失败（网络、身份验证、无远程），请使用底部的后备。

### 2. 检查 `<base>` 上未推送的本地提交

```bash
git log origin/<base>..HEAD --oneline
```

- **空输出：** 设置 `BASE_REF=origin/<base>` 并继续步骤 3。
- **非空输出：** 显示提交列表并询问（根据 `SKILL.md` 中的“询问用户”约定）：

  > “本地`<base>`有N个未推送的提交不在`origin/<base>`上。将它们带到新的功能分支上，还是将它们留在本地`<base>`？”

  - **结转** → `BASE_REF=HEAD`。新分支从本地HEAD开始，保留提交。
  - **沿 `<base>`** → `BASE_REF=origin/<base>` 出发。新的分支开始干净；提交保留在本地 `<base>` 上。

  永远不要默默默认——将外部提交带入 PR 比再次询问更糟糕。

### 3. 创建功能分支

```bash
git checkout --no-overwrite-ignore -b <branch-name> "$BASE_REF"
```

如果由于未提交或忽略的文件将被覆盖而检出失败，请停止并要求用户处理冲突路径。在`mode:pipeline`中，无需询问即可举报拦截者。不要隐藏或删除冲突路径。

## 获取失败后备

如果`git fetch`失败，则从当前本地HEAD分支：

```bash
git checkout -b <branch-name>
```

请注意，在面向用户的摘要中，未验证基础新鲜度。跳过未推送的提交检查 - 如果没有新的 `origin/<base>`，答案是不可靠的。
