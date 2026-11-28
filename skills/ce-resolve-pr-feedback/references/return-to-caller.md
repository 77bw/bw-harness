# 返回呼叫者

在调用者的继承范围下准备审核反馈，并保留判断的批次以便在调用者发布后完成。解析器拥有判断、修复、本地验证、修复拥有的提交和保存的操作。它从不催促，也从不提出阻碍性的问题。调用不能扩大调用者的权限；合并、变基、强制推送和CI批准仍然被排除在外。

全面且有针对性的反馈范围保留了他们现有的判断和修复流程。代码修复批处理返回时其整个远程尾部处于待处理状态，包括不需要自行修复的操作。无更改批次可以通过完整模式现有的 reply/resolve 协议立即完成。它的记录将已验证的完成与不完整的写入或解析区分开来。人类的决定保留了标题的类型化 `needs-human` 有效负载并保持开放。

## 编辑前准备好目的地

从包含该技能的 `SKILL.md` 的绝对目录运行捆绑的助手；在每个 shell 调用中设置锚点，因为 shell 状态不会持久。预检发生在编辑之前，而不是提交之后：

```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pending-feedback.py" preflight
```

当调用提供 `handoff:<path>` 时，将 `--path '<caller path>'` 附加到该命令，保留实际参数。预检拒绝现有目标，包括悬空符号链接，并探测其父目录中的独占临时文件创建。如果没有提供路径，它会分配一个私有操作系统临时目录并返回未使用的 `pending.json` 路径。保留返回的绝对`handoff`路径。技能完成后请勿清理；调用者拥有保留权。

如果预检失败，请在编辑之前停止并返回阻塞项。不要用其他目的地替换被拒绝的呼叫者路径。创建也拒绝覆盖，因此无法替换准备期间出现的目的地。

## 保存判断的批次

捕获 PR 的主机、基础存储库、编号和规范 URL，以及从获取的 PR 元数据中获取的实际头存储库和头引用。头存储库可能与分叉上的基础存储库不同PR；不要从结帐的默认远端推断它。

对于批量创建更改，验证组合修复并仅提交其拥有的更改，如完整模式步骤 5-6 所定义。记录实际的完整提交 SHA。不要推。从每个项目的判断结果中保留最终准确的回复正文，包括多行 Markdown 和记录的提交引用。将类修复的每个覆盖源保存为其自己的操作。整批延迟适用于回复、人工确认、决议和 PR 主体清单勾选等。

对于无更改批次，将 `fix_commit` 设置为 `null` 并在输入现有远程尾部之前保存准备好的操作。检查点在成功写入和返回后观察进度。如果后面的写入失败，则保留之前验证的进度并使用阻塞项返回`pending`；不要声称整批已完成。现有的 `resolution-pending` 线程携带其可见的已提交回复 ID 和正文，因此其保存的操作仅需要缺少的解决方案。

在单独的私有输入文件中构建版本化的 JSON 记录。源指纹是原始获取的正文的小写 SHA-256，编码为 UTF-8，由工具根据解码的正文计算，而不是根据释义发明或计算。助手必须读取原始文件字节；在验证收到的记录之前，请勿重新输入或规范化该记录。

```json
{
  "schema_version": 1,
  "status": "pending",
  "pr": {
    "host": "github.com",
    "base_repo": "upstream/project",
    "number": 42,
    "url": "https://github.com/upstream/project/pull/42",
    "head_repo": "contributor/project",
    "head_ref": "fix/review"
  },
  "fix_commit": "<全小写 40 个字符 SHA，或 null（当没有修复提交时）>",
  "verification": {
    "command": "<命令实际运行，或未运行时为空>",
    "outcome": "passed",
    "details": "<结果和任何预先存在的故障>"
  },
  "actions": [
    {
      "source": {
        "kind": "thread",
        "id": "<稳定获取反馈ID>",
        "url": "https://github.com/upstream/project/pull/42#discussion_r11",
        "body_sha256": "<原始源体的SHA-256>"
      },
      "root_comment_id": 11,
      "thread_id": "<权威的 GraphQL 线程ID>",
      "verdict": "fixed",
      "reply_body": "> Original feedback\n\nExact prepared response.",
      "resolve": true,
      "decision_context": null,
      "invariant_key": "<稳定的根密钥，或 null>"
    }
  ],
  "body_ticks": [
    {"original": "- [ ] P1 — exact finding", "checked": "- [x] P1 — exact finding"}
  ],
  "residuals": []
}
```

- `status` 是 `pending`，直到验证每个符合条件的已保存对话操作已完成，然后是 `completed`。已完成的批次仍可能携带人类残留物，其线程有意保持打开状态。
- `verification.outcome`为`passed`、`pre-existing-failure`、`failed`或`not-run`；保留实际结果，切勿用成功替换不可用的验证。
- `source.kind` 是 `thread`、`comment` 或 `review`。非线程操作具有 null `root_comment_id` 和 `thread_id` 以及 `resolve:false`。 ID 是字符串； REST root/reply ID 是正整数。
- `verdict` 使用现有的 `fixed`、`fixed-differently`、`replied`、`not-addressing`、`declined` 或 `needs-human` 值。 `needs-human` 具有 `resolve:false` 以及标题中完整的 `decision_context`；其他判决的决策上下文无效。
- `residuals` 包含该评分细则的精确类型 `needs-human` 对象，并覆盖所有`sources`、`decision_context` 和 `thread_urls`。也承担现有的未解决的人类决定。不要将它们简化为散文摘要。
- `body_ticks`携带完全相同的原始子弹及其检查版本，仅将`[ ]`更改为`[x]`。空数组意味着没有计划的身体突变。
- 可选动作`progress`保留观察到的`reply_id`、`reply_url`和`resolved`；可选勾选 `progress` 包含 `applied`。省略未观察到的字段。进度是一个检查点，而不是覆盖 GitHub 当前状态的证据。

从输入文件创建切换：

```bash
SKILL_DIR="<absolute path of the directory containing the ce-resolve-pr-feedback SKILL.md>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/pending-feedback.py" create --input '<prepared JSON file>' --path '<preflight handoff path>'
```

帮助器验证原始字节，使用私有权限专门创建目标，将其读回并返回 `{handoff, record}`。只有成功后，准备工作才算完成。 `validate --path '<handoff path>'` 读取并验证现有记录。 `checkpoint --input '<updated JSON file>' --path '<handoff path>'` 以原子方式保存进度、状态和残差，同时保留准备好的 PR、修复 SHA、验证、源身份、准确回复和勾选意图。这些命令永远不会改变GitHub。

如果保存或检查点失败，请报告实际的本地提交和任何观察到的远程成功，以及精确的失败。不要丢失一般失败状态背后的修复 SHA 或将不可读的记录描述为可用的切换。

## 结构化调用者结果

将此结果作为该技能的最后输出。它结束了技能，而不是呼叫协调者的回合；调用者在同一会话中继续执行下一步。

```json
{
  "status": "pending",
  "handoff": "<绝对可读的经过验证的文件路径，如果不可用则为 null>",
  "fix_commit": "<实际修复SHA，或null>",
  "changed_files": ["<fix-owned paths>"],
  "verification": {"command": "<actual command>", "outcome": "passed", "details": "<actual result>"},
  "residuals": [],
  "blockers": []
}
```

确切的结果状态是 `pending`、`completed` 和 `incomplete-handoff`。使用 `pending` 进行已验证的已保存批次，其中包含延迟或不完整的对话工作，`completed` 仅用于验证的无更改完成情况，以及 `incomplete-handoff` 当不存在可用的已保存记录或其最新观察到的进度无法进行检查点时。即使其他操作完成，也会返回类型化的人类残差。不问问题就说出阻止者的名字。

调用者保留该文件，发布记录的修复而不重写其 SHA，并将保存的路径返回给解析器以供稍后完成对话。仅靠推送并不能完成审核对话。此准备模式返回时不执行任何调用者步骤。
