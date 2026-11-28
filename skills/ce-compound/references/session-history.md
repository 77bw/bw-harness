# 会话历史记录（第 1 阶段第 4 步）

会话历史记录是第一阶段的最终输入，而不是工作流程停止。当它返回时，包括“没有相关的先前会话”，直接进入表单选择，无需暂停或总结。

## 会话上下文

在第 1 阶段会话历史记录过滤之前，使用 shell 工具在运行时解析两个值。将每个命令作为自己的命令运行并读取其退出状态。非零退出是这里的正常状态，而不是路由错误：

- **Git分支**：运行`git rev-parse --abbrev-ref HEAD`。使用分支名称来过滤阶段 1 中的会话历史记录。如果它返回 `HEAD` （分离）或以非零值退出（不是 git 存储库），则跳过分支过滤。
- **仓库根目录**：运行`git rev-parse --show-toplevel`。将其用作阶段 1 中的会话历史记录存储库过滤器。如果它以非零值退出（不是 git 存储库），则回退到工作目录。

#### 4. **会话历史记录**（调度相关文档查找器后的内部流程；在完整模式下自动，包括非交互式）
   - 这是一个两阶段的探测：下面的廉价发现+元数据传递始终执行，而昂贵的提取+合成仅在探测清除相关栏时执行（请参阅下面的**升级检查**）。
   - 使用 `scripts/session-history/` 直接在此技能中运行会话发现、branch/keyword 过滤、扫描窗口选择、深度选择和每会话提取。
   - 阅读`references/agents/session-historian.md`处的技能本地合成提示，然后使用该提示内容调度通用子代理。不要在 type/name 之前派遣独立代理。

   **保持会话历史记录负载紧密。** 长且关键字丰富的负载会邀请流程扩大其搜索范围。使用这个形状：

   - **会话上下文**（仅当上面的值完全解析时；否则省略）：存储库名称，当前 git 分支。
   - **时间窗口**：显式`7 days`，除非记录的问题明显跨越更长的弧线。
   - **问题主题**：一句话命名具体问题 - 错误消息、模块名称、发生了什么问题以及如何修复。不是一个段落；不是相关主题的项目符号列表。
   - **过滤规则（一行）**：“仅与此特定问题直接相关的表面发现。忽略来自同一会话或分支的不相关工作。”
   - **输出架构**：

     ```
     使用以下部分构建您的回答（忽略任何没有发现的内容）：
     - 之前尝试过什么
     - 什么不起作用
     - Key decisions
     - Related context
     ```

   不要附加额外的上下文块、排除列表或主题关键字项目符号。详细的有效负载使会话历史记录流不断扩大搜索范围，从而迅速增加了占用时间。如果需要关键字搜索，内部流程会根据主题来决定。
   - 返回结构化摘要，或 `no relevant prior sessions`。两者都是有效的最终阶段 1 输入，如果是后者，则在没有会话上下文的情况下编写文档。

   **脚本解析。** 将`SKILL_DIR`设置为您刚刚读取的包含SKILL.md的目录的绝对路径，并从`"$SKILL_DIR/scripts/session-history/"`运行捆绑的脚本。在下面的每个 bash 块中内联设置 `SKILL_DIR` （shell 状态在命令之间不会持续）。如果捆绑脚本确实不存在于`"$SKILL_DIR/scripts/session-history/"`下的磁盘上，请明显跳过会话历史记录：“在此技能的目录中未找到会话历史记录捆绑脚本；跳过本次运行的会话历史记录探测。”在没有会话上下文的情况下继续第 2 阶段。

   **发现管道。** 从问题主题推断扫描窗口，从 7 天开始。运行发现和元数据提取：

   ```bash
   SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
   if [ -f "$SKILL_DIR/scripts/session-history/discover-sessions.sh" ] && [ -f "$SKILL_DIR/scripts/session-history/extract-metadata.py" ]; then
     PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
     REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd); REPO_NAME=$(basename "$REPO_ROOT"); SCAN_DAYS="7"; bash "$SKILL_DIR/scripts/session-history/discover-sessions.sh" "$REPO_NAME" "$SCAN_DAYS" --cwd "$REPO_ROOT" | tr '\n' '\0' | xargs -0 "$PY" "$SKILL_DIR/scripts/session-history/extract-metadata.py" --cwd-filter "$REPO_ROOT";
   else echo "Session history bundled scripts were not found in this skill's directory; skipping the session-history probe for this run."; fi
   ```

   该命令打印JSONL。 `xargs` 可以将长文件列表拆分为多个脚本运行；每次运行都会为每个保留会话打印一个对象，然后打印它自己的 `_meta` 行。一次一行地解析输出，因为整个流不是一个 JSON 文档。通行证的 `files_processed` 总数是其 `_meta` 条线的总和； `--keyword` 重新运行是一个新的过程，而不是更多的文件。可选字段被省略，未设置为 null，因此缺少键不是错误。新近度排名`last_ts`，回落至`ts`。如果您使用代码处理输出，请先查看几行并使用您看到的键。

   Claude 会话位于 `~/.claude/projects/` 下，除非设置了 `CLAUDE_CONFIG_DIR`，在这种情况下，它们位于该目录的 `projects/` 下。 Codex 会话位于 `~/.codex/sessions/` 下，除非设置了 `CODEX_HOME`，在这种情况下，它们位于该目录的 `sessions/` 下； `~/.agents/sessions/` 也被扫描。当存在于 `~/.pi/agent/sessions/`（`PI_CODING_AGENT_DIR` / `PI_CODING_AGENT_SESSION_DIR` 覆盖）下时，包含 Pi 会话，以及 `~/.omp/agent/sessions/` 下的 oh-my-pi (`omp`) 会话（命名配置文件：`~/.omp/profiles/<name>/agent/sessions/`；XDG：`$XDG_DATA_HOME/omp/sessions` 和 `$XDG_DATA_HOME/omp/profiles/<name>/sessions`；`PI_CONFIG_DIR` / `PI_CODING_AGENT_DIR` / `PI_CODING_AGENT_SESSION_DIR` 覆盖）。 Claude、Codex、Pi 和 oh-my-pi (`omp`) 会话携带记录的 `cwd`（Claude 也有 git 分支；Pi/omp 没有）。当该 cwd 是存储库根、其祖先或其内部路径时，`--cwd-filter` 会保持会话（路径组件边界：`my-repo` 与 `my-repo-old` 不匹配）。没有记录 cwd 的 Claude、Codex、Pi 和 omp 会话将被丢弃。光标没有 cwd 并保持不变。不要删除 Claude 会话，因为其项目文件夹名称缺少存储库基本名称。这就是 Claude 存储家长启动的会话的方式。如果第一遍的`files_processed`总数为`0`，则返回`no relevant prior sessions`。如果第一遍没有找到相关分支匹配，或者如果处理 Codex、Pi 或 oh-my-pi (`omp`) 会话，则从主题中派生 2-4 个关键字，并使用 `--keyword K1,K2,...` 重新运行元数据提取。在 Claude Code、Codex、Cursor、Pi 和 oh-my-pi (`omp`) 中保留最多 5 个会话，按分支匹配、关键字匹配计数、文件大小超过 30KB 和新近度排名。排除当前会话。

   **升级检查。** 上面的发现+元数据传递是廉价的探针，并且始终在完整模式下运行。仅当至少一个保留的候选清除了相关栏时，才升级到下面的提取和合成阶段：当前分支匹配，或 ≥2 个主题关键字匹配。如果没有候选人清除栏（包括`files_processed`总计`0`），则在此停止，将`no relevant prior sessions`记录为会话历史输入，并跳过提取和合成。这项检查使常开探头保持廉价。仅当先前的会话真正相关时才会运行昂贵的综合。

   **提取管道。** 创建`SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/ce-compound-sessions-XXXXXX")`。对于每个选定的会话，将提取的内容写入临时文件：

   ```bash
   SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
   if [ -f "$SKILL_DIR/scripts/session-history/extract-skeleton.py" ]; then
     PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
     "$PY" "$SKILL_DIR/scripts/session-history/extract-skeleton.py" --output "$SCRATCH/<session-id>.skeleton.txt" < <session-file>;
   else echo "Session history bundled scripts were not found in this skill's directory; skipping the session-history probe for this run."; fi
   ```

   当死胡同或重复出现的错误可能有用时，有选择地使用`extract-errors.py`。仅将临时文件路径和元数据传递给合成子代理。

   **综合调度。** 构建一个通用子代理提示，其中包含：
   - `references/agents/session-historian.md`的全部内容
   - `problem_topic`
   - `scratch_dir`
   - 包含提取的文件路径和元数据的 `sessions` 数组
   - 上面的输出模式
   - 上面的过滤规则

   子代理仅读取临时路径，**将其散文结果写入`{run_dir}/session-history.md`，并在确认写入后仅返回该产物路径**（同样的#956可靠性原因适用，因为会话历史记录结果是容易导致摘要崩溃的长篇散文）。如果 `{run_id}` 未解析或产物写入失败，它将返回内联散文（根据上面的内联回退规则）。如果合成失败，请记下失败并在没有会话上下文的情况下继续。
