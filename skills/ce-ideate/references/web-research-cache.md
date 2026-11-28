# 网络研究缓存

在调度 `web-researcher` 之前检查缓存时，或者在调度后将新的研究附加到缓存时，请阅读此内容。这里的行为是有条件的——大多数调用要么命中缓存，要么写入一次然后继续。

## 缓存文件形状

```json
[
  {
    "key": {
      "mode": "repo|elsewhere-software|elsewhere-non-software",
      "focus_hint_normalized": "<小写、空格折叠焦点提示或空字符串>",
      "topic_surface_hash": "<用户提供的主题表面的短哈希>"
    },
    "result": "<网络研究人员输出为纯文本>",
    "ts": "<iso8601>"
  }
]
```

文件位于 `<scratch-dir>/web-research-cache.json` 下，其中 `<scratch-dir>` 是 `<scratch-root>/ce-ideate/<run-id>`，在 `references/grounding.md` 第 1 阶段解决一次。

## 重复使用检查

在分派 `web-researcher` 之前，解析 bash 中的暂存根（`<scratch-dir>` 的父级）并列出同级 run-id 目录 - 会话中的细化循环可以按主题（而不是运行 id）合法地重用另一个运行的缓存：

```bash
SCRATCH_DIR="<absolute scratch-dir resolved in Phase 1>"
SCRATCH_ROOT="$(dirname "$SCRATCH_DIR")"
find "$SCRATCH_ROOT" -maxdepth 2 -name 'web-research-cache.json' -type f 2>/dev/null
```

当不存在缓存文件时，`find` 以空输出退出 0，因此首次运行情况不会中止重用检查步骤。

读取每个匹配的文件。如果任何条目的 `key` 与当前调度匹配（相同的完整模式变体 — `repo`、`elsewhere-software` 或 `elsewhere-non-software` — 加上相同的不区分大小写的标准化焦点提示以及相同的 `topic_surface_hash`），则跳过调度并将缓存的 `result` 传递到统一的基础摘要。模式变体必须完全匹配：`elsewhere-software`和`elsewhere-non-software`是不同的域，不得交叉重用。摘要中的注释：“重复使用本次会议之前的网络研究 - 说‘重新研究’来刷新。”

在 `re-research` 覆盖时，删除匹配的条目并重新分派。

## 新交付后追加

重新调度后，使用阶段 1 中的绝对路径将新结果附加到当前运行的缓存文件中的 `<scratch-dir>/web-research-cache.json`（如果需要，创建目录和文件）。会话中的下一次调用可以通过上面的 `find` 列表重用它。

## 主题表面哈希

`topic_surface_hash` 对网络研究所依据的用户提供的内容进行哈希处理。该内容是：
- **其他模式（`elsewhere-software`、`elsewhere-non-software`）：**用户的主题提示加上任何 0.4 阶段摄入答案（代理正在研究的实际主题）。这两个子模式是单独键入的 - 由于研究领域不同，同一主题哈希的软件和非软件之间的重新分类必须强制进行新的调度。
- **回购模式：**焦点提示加上稳定的回购鉴别器。当焦点为空时，这使缓存键保持有意义——同一存储库中的两个裸提示调用合法地共享研究，但该键仍然区分存储库。由于每个存储库中的缓存文件现在都在共享操作系统临时根下运行，因此像 `app` 或 `frontend` 这样的裸基名会在不相关的存储库之间发生冲突。使用此后备链解析鉴别器并对结果进行哈希处理（sha256 的前 8 个十六进制字符就足够了）：
    1. `git remote get-url origin` — 跨机器稳定，适用于同一远程的协作者。
    2. `git rev-parse --show-toplevel` — 绝对仓库路径；机器本地但始终可在 git checkout 中使用。
    3. 当前工作目录的绝对路径——不在 git 存储库中时的最后手段。

散列之前标准化：小写，折叠空格。 （存储库鉴别器哈希是根据原始命令输出计算的；仅焦点提示和主题文本被标准化。）

## 降解

如果在当前平台上的调用之间无法访问缓存文件（文件系统隔离、沙箱、临时工作目录），则降级为“不重用，每次都调度”。请注意综合基础摘要中的限制，并在不重用的情况下继续进行，而不是发明平台可能不具备的功能。
