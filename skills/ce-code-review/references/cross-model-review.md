# 跨模型对抗通行证

通过不同的模型（“同行”）第二次运行 **对抗性** 审查，通过一条固定路线，以只读过程进行。对等方获得与正在进行的审查者使用的 **相同* `references/personas/adversarial-reviewer.md` 简介，返回相同的 `findings-schema.json` 形状，并作为审查者 `adversarial-<provider>` 加入第 5 阶段（综合）。仅当其身份记录（“收据”）显示 `independence_verified: true` 时，其发现才算作独立佐证，并且可以促进两个评审员都同意的发现。否则，其调查结果将作为证据保留在审查中，而不会获得晋升奖金。

此通行证是**仅限对抗性**。没有其他角色拥有跨模型双胞胎，也没有完全不同的通才同行。除非第 3 阶段（审稿人选择）已经选择了对抗性审稿人，否则该通行证不需要任何费用。

在任何审阅的内容离开机器之前，主机会选择一条具体路线并批准它（本文档将该批准称为“制裁”）。 `scripts/cross-model-adversarial-review.sh` 保留该固定路线，应用只读控件，在结果模式形状中捕获JSON，并记录身份收据。在分发之前，它会对 diff 的令牌计数和文件计数进行保守估计。过大的差异不会整个粘贴到提示中：工作人员向对等方提供编排器的紧凑语义审查图，并将确切的差异保留为存储库外部的私有文件。每个路由获取该文件的路径并有选择地读取它（`references/cross-model-recovery.md`记录每个路由可以读取的内容）。每条路由都经过 acpx，它需要 Node 22.13 或更高版本且`npx`。失败的路由不会写入任何产物，也不会自行切换收件人。

## 运行条件——仅当全部成立时才运行

1. `adversarial-reviewer`在第3阶段（审稿人选择）中被选中，或者审稿深度门选择了聚焦路径，其一个独立的读取就是这个镜头。重用该选择；不要在微不足道的差异上运行昂贵的外部CLI。
2. 工作树是已审查的头（独立、`base:`或`local-aligned`范围）。跳过`pr-remote`/`branch-remote`：同行评审本地树，这不是PR或分支头。

## 步骤 1 — 证明主机身份，然后批准一条固定路由

将请求的 **目标**、CLI **harness/intermediary**、服务 **family/provider** 和服务模型分开。 `cursor` 表示 `cursor-agent` 及其配置的 default/Auto 模型，并且没有 `--model` 标志。 `composer` 表示通过 Cursor 的显式 Composer 系列模型。 `grok`更喜欢它的原生CLI；通过 Cursor 的 Grok 是一条独特的路线和接收者。 `antigravity` 表示通过 Google 的 Antigravity ACP 运行时构建的 Gemini 模型；对 Gemini 对等点的请求绑定目标 `antigravity`。 `pi` 表示 Pi 编码代理在其自己配置的模型上，除非 `provider/model` 引脚指定了一个； Pi 为任何提供者提供服务，因此 `pi` 同级的服务家庭是未知的，并且其审查从来都不是独立的。

证明宿主宿主及其服务家族：

```bash
XHOST_SEEN=;
if [ "${CLAUDECODE:-}" = "1" ]; then XHOST_SEEN="$XHOST_SEEN claude"; fi;
if [ -n "${CODEX_SANDBOX:-}${CODEX_SANDBOX_NETWORK_DISABLED:-}${CODEX_SESSION_ID:-}${CODEX_THREAD_ID:-}${CODEX_CI:-}" ]; then XHOST_SEEN="$XHOST_SEEN codex"; fi;
if [ "${GROK_AGENT:-}" = "1" ] || [ -n "${GROK_SESSION_ID:-}" ]; then XHOST_SEEN="$XHOST_SEEN grok"; fi;
if [ -n "${OMPCODE:-}" ]; then XHOST_HARNESS=omp; XHOST_FAMILY=unknown;
elif [ "${CROSS_MODEL_HOST_HARNESS:-}" = pi ]; then XHOST_HARNESS=pi; XHOST_FAMILY=unknown;
elif [ "$XHOST_SEEN" = " claude" ] || [ "$XHOST_SEEN" = " codex" ] || [ "$XHOST_SEEN" = " grok" ]; then XHOST_HARNESS="${XHOST_SEEN# }"; XHOST_FAMILY="$XHOST_HARNESS";
elif [ -n "$XHOST_SEEN" ]; then XHOST_HARNESS=unknown; XHOST_FAMILY=unknown;
elif [ -n "${CURSOR_AGENT:-}${CURSOR_CONVERSATION_ID:-}" ]; then XHOST_HARNESS=cursor; XHOST_FAMILY=unknown;
elif [ -n "${OPENCODE_TERMINAL:-}" ]; then XHOST_HARNESS=opencode; XHOST_FAMILY=unknown;
else XHOST_HARNESS=unknown; XHOST_FAMILY=unknown; fi
```

将`XHOST_HARNESS`传递为`CROSS_MODEL_HOST_HARNESS`；传递 `XHOST_FAMILY` 作为第一个工作参数。该片段是证据，而不是结论：它解析了其环境标记已命名的宿主，并且在您可以从自己的运行时识别的宿主上产生`unknown`，证明您所知道的。代码片段未命名的宿主此处不需要新分支。两个令牌都必须是工作人员接受的对等密钥，而不是提供商的公司名称。家庭为 `codex`、`claude`、`grok`、`composer`、`gemini` 或 `unknown`。宿主为 `codex`、`claude`、`grok`、`cursor`、`opencode`、`antigravity`、`omp`、`pi` 或 `unknown`。任一槽中的公司名称（例如 `anthropic`、`openai` 或 `xai`）都会使工作人员拒绝该工作并且不会写入任何产物。

Claude Code、Codex 和 Grok 各自服务于自己的模型系列，因此当该宿主的标记是唯一存在的此类标记时，该片段会从该系列中获取该系列。另一个宿主可以复制这些标记之一（oh-my-pi 设置 `CLAUDECODE=1` 无论模型为其提供服务），并且从另一个宿主内部启动的会话会继承该宿主的标记。因此，该片段将家庭 `unknown` 留在为任何模型（oh-my-pi 或 Pi）提供服务的宿主上，或者当存在多个标记时。将片段名称传递给家人。当代码片段产生harness `omp`或`pi`时，仍然传递`unknown`并开始工作：worker从harness会话记录的模型中读取服务族，并在没有指定第一方模型时跳过。在其他地方，当代码片段离开系列 `unknown` 时，仅从运行时发布的模型 ID 设置它作为服务于该会话的模型，并且仅当该 ID 映射到 `codex`、`claude`、`grok`、`composer` 或 `gemini` 时。请求的型号、该型号自己的声明以及产品名称都不是该 ID。切勿从 Cursor 品牌推断服务家庭。否则，未知的寄宿家庭无法通过自动同族检查，因此跳过自动跨模型检查。

<!-- ce-config-layers:start -->
**解析两个存储库文件中的普通 CE yaml 密钥。**

- **读取** `<repo-root>/.compound-engineering/config.local.yaml`，然后读取 `config.yaml` (`<repo-root>` = `git rev-parse --show-toplevel`)。丢失的文件将被跳过。 Gitignore 不会改变分辨率。
- **以第一个活动（未注释）值获胜**。对于标量，未设置空；无效值继续下一层，则技能默认。对于列表和地图，现有的键（包括空列表或地图）将替换整个键。
- **不要**将此规则用于 `docs_root` — 该键仅是 `config.yaml`。
<!-- ce-config-layers:end -->

**检查发送内容的策略 - 首先评估。** 在普通密钥规则下从相同的两个存储库 CE 配置文件中读取 `cross_model_review_mode:`。有效值为`auto`（默认）和`off`；其他任何内容都无效并继续到下一层，然后是`auto`。当它解析为 `off` 时，在同行解析、披露或任何作业开始之前跳过此处的自动跨模型传递。一个例外是当用户在对话中明确请求跨模型对等方运行时； `cross_model_peer` 值或项目指令偏好不是选择加入。将跳过原因记录为**由签出配置禁用**，这与不可证明的主机或不可用或非独立路由的原因不同。进程中的 `adversarial-reviewer` 保持镜头与任何从未开始的同行完全相同。实时用户禁止仍然优先于 `auto`。此通道的跳过和目标选择键是`cross_model_review_mode`和`cross_model_peer`。丢失文件或未设置密钥采用默认自动路由；他们不是跳过者。另一个技能的引擎偏好不是这个门。模型和工作覆盖与参考状态的绑定目标保持一致。

按此顺序解决首选项：

1. 用户**在对话中陈述**的偏好（例如“使用 grok 进行跨模型传递”）。
2. `cross_model_peer:` 来自两个 repo CE 配置文件（`config.local.yaml` 然后`config.yaml`）。应用普通键规则：第一个主动支持的目标获胜；无效值继续到下一层，然后是步骤 3。
3. 您的**项目说明**（上下文中的活动指令）中已有的首选项 - 从上下文中使用，**从不**从命名文件中读取。
4. **默认值：** `codex → claude → grok → antigravity` 中第一个可用的已证明不同目标。 Cursor default 和 Composer 仅在步骤 1-3 之一命名时运行。

在发送任何内容之前，将目标解析为一个具体安装的路由，公布它，并将其作为`CROSS_MODEL_FIXED_ROUTE`传递。 `CROSS_MODEL_PEERS` 是可选的出口限制，而不是必需的批准。设置后，每个收件人（目标和中介）都必须在下面的别名规则下被它允许，并且它不允许的收件人是指定的跳过。否则，当它未设置或为空时，不会过滤任何收件人并继续传递；调用此技能加上发送前所做的披露即为批准。不要检查工人来源来重新发现这一点；它完全执行了这个合同。 `CROSS_MODEL_FIXED_ROUTE` 完全接受这些标记。工作人员拒绝任何其他内容，并且不编写任何产物，包括像 `codex-cli` 这样的路线形状的猜测：

| 目标 | 路由令牌 |
|--------|----------------|
| `codex` | `codex` |
| `claude` | `claude` |
| `grok` | `grok-cli`（原生CLI）或`grok-cursor`（通过 Cursor 中介） |
| `cursor` | `cursor` |
| `composer` | `composer` |
| `opencode` | `opencode` |
| `antigravity` | `antigravity` |
| `pi` | `pi` |

主机宿主不选择 Grok 路线。安装 CLI 后，目标 `grok` 会绑定 `grok-cli`。仅当用户通过 Cursor 请求 Grok 时，或者当 grok CLI 不存在且 Cursor 是受制裁的接收者时，才绑定 `grok-cursor`。

失败的路由不会返回任何产物，也不会自行更改提供者或中介。重试同一已解决的路线将保留其现有的制裁和披露；更改路线或任何收件人需要新的决议、制裁和交付前的披露。只有在路由适配器报告提供者过载（HTTP 529）作为提示错误类型`overloaded`之后，工作人员才可以重复相同的路由一次；它使接收者、模型、范围和共享对等截止日期保持固定。今天只有克劳德适配器报告了这种形式；其他适配器在内部重试重载，因此从它们到达工作线程的过载会以普通故障结束。为了向后兼容，`CROSS_MODEL_PEERS`中的`cursor`或`composer`都认可Cursor作为中介，但选择Cursor-default需要目标`cursor`； `grok` 永远不会单独制裁 Grok-via-Cursor。反重力路线仅受字面`antigravity`认可； `CROSS_MODEL_PEERS`中的`gemini`什么也不承认。

**签出配置的模型和工作。**解析目标后，在普通密钥规则下从相同的两个存储库CE配置文件中读取`cross_model_model:`和`cross_model_effort:`。当`cross_model_model`设置时，传递`CROSS_MODEL_MODEL_OVERRIDE_TARGET=<resolved-target>`和`CROSS_MODEL_MODEL_OVERRIDE=<value>`；当`cross_model_effort`设置时，传递`CROSS_MODEL_EFFORT_OVERRIDE=<value>`。两者都使用下面启动调用的 `env` 前缀。工作人员根据其实际运行的路线检查每个值。模型必须属于已解析目标自己的系列：别名（如 `fable`）或完整 ID（如 `claude-opus-5-5` 代表 `claude`）； `gpt-*` 代表 `codex`，可选择命名空间限定，例如 `openai.gpt-6.1-sol`，当 CLI 通过非默认 `model_provider` 路由时； `gemini-*` 为 `antigravity`； `provider/model`适用于`opencode`和`pi`。努力必须是路线适配器提供的级别；对于`antigravity`，这是它的思维水平，`low`，`medium`，或`high`，对于`opencode`（2.x），它是`none`到`max`，如模型列出的那样。光标代理和`pi`路线不接受任何努力覆盖。不兼容的值会以指定的跳过原因停止传递；工人永远不会替代。取消设置键会使脚本的编辑映射保持不变。完全按照要求在步骤 3（宣布）行中宣布配置的模型和工作量。用户在对话中陈述的模型或工作比配置键更重要。

首先运行首选映射。只有在观察到不可用、过时或不兼容的模型后，主机才可以选择最接近的兼容same-target/same-family替代品。将其与`CROSS_MODEL_MODEL_OVERRIDE_TARGET=<target>`和`CROSS_MODEL_MODEL_OVERRIDE=<model-id>`绑定。切勿跨系列替换、将覆盖泄漏到另一条路线、悄悄更改显式模型或添加接收者。

目标`antigravity`从不接受主机选择的替换。其工作人员请求 Gemini 4 Argon，当账户不提供 Argon 时，会在发送任何提示之前退回到 Gemini Flash；运行日志命名所使用的模型。配置的 `antigravity` 模型完全运行，否则过程会跳过。

法典工作人员以同样的方式对待自己的编辑请求。当帐户不提供默认模型时，它会在发送任何提示之前回退到备用模型。当适配器拒绝编辑推理工作时，它会在没有编辑推理的情况下重试一次并记录`effort_requested: unverified`。配置的 Codex 模型或工作会完全运行，否则会跳过传递。

## 第 2 步 — 提供者模型 + 推理层（在脚本中定义）

对等点在**每个提供者一个编辑选择的模型和推理层上运行**。具体模型 ID 和路线工作量标志位于 `scripts/cross-model-adversarial-review.sh` 的一个映射中；本文不再重复它们。 Codex、Claude Opus、Antigravity 目前使用率较高；原生 Grok 使用超高。光标代理 Grok 路线使用 Cursor 的 high/fast 预设，因为 Cursor 为每个模型提供一个预设；作曲家的快速层是它的天花板。用户选择对等目标，并可以通过`cross_model_model` / `cross_model_effort` 固定该目标的模型和努力（步骤1）；该脚本会验证并且不会替代。切勿继承宿主配置的默认模型。仅在评估显示发现相同问题后才采用较低层，而不仅仅是考虑成本。

剧本总是使用对抗性人物简介；折叠力 `reviewer` 至 `adversarial-<provider>`。

## 第 3 步 — 宣布

一旦进行此公开，调用 ce-code-review 是对所选、配置和列入白名单的路由的授权。该公告是通知，而不是第二次确认提示。仅在明确的用户禁止、没有实时选择加入的结帐 `cross_model_review_mode: off` 或观察到的范围、白名单或路由失败时跳过。切勿仅仅因为用户没有在同一提示中单独授权外部通行证而跳过。

预调度资格基于已安装的路线存在和制裁，而不是凭证状态。在提供程序支持的启动之前不要运行身份验证探测；只有在提供者能够调度之后，身份验证才是权威的。

- **交互式主机，默认模式：**打印一条**突出的独立行**，将其框架为**独立的跨模型对抗性审查**（说“跨模型”/“独立模型”，而不是内部“同行”行话）。该行从脚本内映射中命名请求的 **模型和推理级别**，并声明已审核的 code/diff 内容已发送到该提供者。对于光标代理路由，它命名**路由以及模型**，因为两个不同的模型可以通过*相同* `cursor-agent` CLI到达。 **一个披露条件控制着公告以及以后每次提及对等点：** 按目标和请求的模型和工作来命名它，作为请求（“在 <effort> 请求 <model>”），而不是作为该模型服务的声明。仅当收据与请求不一致或路线请求无模型时（光标default/Auto表示“服务模型未经验证”），才添加服务警告。具有所请求型号的无收据路线不会有任何警告：`model_actual: unverified` 表示没有收据，而不是未知型号。将线路与第 3 阶段团队公告一起放置，而不是埋在其后。
  - 仅当寄宿家庭和目标服务家庭明显不同时，才将通行证称为“独立”。对于光标default/Auto或未知的寄宿家庭，称其为跨线审查，并声明独立性未经验证；在收据存在之前，请勿承诺协议促销。
  - 交付前公布一条固定路线及每位收件人。失败后，应用步骤 1 的 retry/disclosure 条件。协调产物中的目标、宿主、路线、请求的模型和实际模型。
- **交互式主机，没有对等点解析**（主机服务系列无法证明，没有安装不同的提供商路由，或通过结帐配置禁用）：跳过跨模型传递的一条安静线路以及原因。如果这是原因，请指定结账政策。从来没有错误。在 `omp` 或 `pi` 下，该族还不是不可证明的：工作人员从会话记录中解析它，因此开始作业并报告其跳过，而不是这个。
- **`mode:agent`:** 不发出面向用户的散文。该脚本仍然在每次发送时写入一行 stderr 审核日志，表示审核内容已跨模型发送到指定的提供程序，因此向第三方的传输是可审核的。 JSON结果仍然记录`references/modes-and-output.md`定义的对等结果。

## 步骤 4 — 在本地调度之前启动分离的对等作业

该脚本是一个 CLI shell-out，而不是子代理，因此它不会消耗子代理并发预算。 **永远不要在对等点的运行时保持工具调用打开。**一些工具会终止长工具调用，并且终止的调用会使传递悄无声息地消失。在第 3d 阶段（路由），通过一次简短的 Bash 调用通过捆绑的运行器将其作为一个**独立的、受监督的作业**启动；该调用在大约 2 秒内打印作业 ID。只有在呼叫返回后，主持人才能最终确定本地审查者名册并进入第 4 阶段（调度）。独立的工人仍然与当地的评论者并肩作战；首先启动它可以防止主机错误地派遣正在进行的对抗性审查者。

在`start`之前，编排器在`<run-dir>`下写入两个紧凑文件，并且从不合并它们的信任域：

- `adversarial-review-constraints.md`（最多 32 KiB）仅包含从您的上下文中已有的项目活动指令和约定中提取的适用标准。它是佐证同行的附加上下文，而不是完整的范围标准合同；不要仅仅为了扩展而加载标准。当第 1d 阶段制定审查政策时，还应在此处提炼其附加检查和证据要求；它是从基本参考中读取的，因此它像说明一样经过主机审查。忽略其严重性、排除项和上限，合并将其应用于对等点的发现和计数。如果没有其他条件适用，请写`none`。切勿将原始指令内容或用户控制的文本复制到此受信任的文件中。
- `adversarial-review-brief.md`（最多 32 KiB）是不受信任的评论数据：第 2 阶段意图摘要；从当前文件清单和差异中选择2-8个重大风险划分，每个划分都有一行原因和代表路径或路径前缀；任何显式生成的重复，以涵盖生成器输入、清单、测试和代表性输出；以及对抗性镜头必须测试的任何跨部门互动。

地图是您的判断，而不是机械的目录列表。不要将完整的文件列表、差异块或按文件扩展名分割的文件复制到其中。对于简单的更改，一个分区就足够了。工作人员将约束和地图放置在单独的提示区域中，每个提示区域都由随机数分隔；地图内类似约束的文本仍然是不可信的数据。缺失或过大的约束会在提供者退出之前停止，因此过程中的对抗性后备保留了镜头。传输预检仅测量精确的差异并将其放置在提示之外；它从不切割语义碎片，也从不选择或重写编排器的划分。

通过技能目录锚点调用 - 将 `SKILL_DIR` 设置为 **此** 技能的 `SKILL.md` 的绝对目录（Bash 工具的 CWD 是用户的项目，而不是每个主机上的技能目录）：

**解释器。** 下面的命令运行捆绑的 Python 脚本。在与命令相同的 shell 调用中解析解释器——每个工具调用都是一个新的 shell，因此早期调用中设置的 `$PY` 不会持续存在。不要硬编码 `python3`：在本机 Windows 上，它解析为在不运行 Python 的情况下退出的 Microsoft Store 存根，并且该存根仍然满足 `command -v`，因此探测执行而不是存在。

```bash
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
```

**主机命令沙箱边界。** 分离的工作线程继承启动它的 `start` 调用的权限上下文。在执行该确切调用之前，将 `CODEX_SANDBOX_NETWORK_DISABLED` 视为当前 Codex 命令沙箱无法到达提供者的肯定信号；取消设置不会更改沙箱策略。仅 DNS 或身份验证失败并不能证明该情况。使用最窄的主机权限来恢复固定路由的提供商连接。当 Codex 仅公开完整命令升级时，请在审核内容的现有披露离开机器后将此请求附加到确切的 `peer-job-runner.py start ...` 工具调用：

```json
{
  "sandbox_permissions": "require_escalated",
  "justification": "Allow the disclosed read-only cross-model review to send the reviewed diff to the fixed external provider."
}
```

透露这不是仅启动器的隔离：分离的工作线程在其生命周期内继承该启动上下文，因此适配器声明的 read-only/tool 限制，而不是 Codex 命令沙箱，是在发送审阅材料时绑定对等点的内容。如果授权被拒绝或不可用，则不执行`start`；保留进程中的对抗性审查者作为后备，并且不创建同行工作。在 `start` 返回作业 ID 后，任何网络、身份验证或提供程序故障都是开始作业结果，并遵循普通的 terminal/recovery 规则；将 `status`、`wait`、`result` 和 `reap` 保留在沙箱中，因为它们不需要提供者连接。

```bash
SKILL_DIR="<absolute path of the directory containing the ce-code-review SKILL.md you read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
echo "peer-deadline-secs=$(( ${CROSS_MODEL_HARD_SECS:-1200} + 10 ))";
CE_PEER_HARD_SECS= CROSS_MODEL_HOST_HARNESS="<host-harness>" CROSS_MODEL_FIXED_ROUTE="<fixed-route>" "$PY" "$SKILL_DIR/scripts/peer-job-runner.py" start --skill ce-code-review --run-id "<run-id>" --label adversarial -- env CROSS_MODEL_HOST_HARNESS="<host-harness>" CROSS_MODEL_FIXED_ROUTE="<fixed-route>" bash "$SKILL_DIR/scripts/cross-model-adversarial-review.sh" "<host-serving-family>" "<target>" "<base-ref>" "<run-dir>"
```

当步骤 1 解析配置的模型或工作时，将 `CROSS_MODEL_MODEL_OVERRIDE_TARGET="<target>" CROSS_MODEL_MODEL_OVERRIDE="<model>"` and/or `CROSS_MODEL_EFFORT_OVERRIDE="<effort>"` 添加到 `CROSS_MODEL_FIXED_ROUTE` 之后的 `env` 前缀；未设置时忽略它们。

三个嵌套时间窗口是由一项设置（“旋钮”）`CROSS_MODEL_HARD_SECS` 控制的一项预算。跑步者自动从环境旋钮（`max(1230, knob + 30)`）获取其监控硬窗口。清除起始前缀 (`CE_PEER_HARD_SECS=`) 上的 `CE_PEER_HARD_SECS`，以便早期会话或宿主导出在环境中留下的陈旧值不会削弱该派生。当技能故意设置 1（ce-work / 海拔）时，显式数字 `CE_PEER_HARD_SECS` 仍然获胜；该路径不得设置。在与 `start` （如上所述）相同的 shell 中将协调器截止日期打印为 `knob + 10`，并使用下面打印的 `peer-deadline-secs=<n>`。永远不要对其进行硬编码：文字在旋钮更改后仍然存在，然后获得健康的对等体。

**不要将`CROSS_MODEL_HARD_SECS`转发给worker。** runner已经通过了周围环境，因此用户实际设置的旋钮会自行到达worker。重新导出 Orchestrator 的“已解析”值会将回退转变为显式覆盖，并剥夺工作线程自身的默认值。

- `<run-id>` = 第 1b 阶段运行 ID（与形成 `<run-dir>` 的 ID 相同）；工作状态位于 `<run-dir>/jobs/<job-id>/` 之下。
- `<host-serving-family>`是`codex`、`claude`、`grok`、`composer`、`gemini`或`unknown`； `<host-harness>` 为 `codex`、`claude`、`grok`、`cursor`、`opencode`、`antigravity`、`omp`、`pi` 或 `unknown`。
- `<target>`是`codex`、`claude`、`grok`、`cursor`、`composer`、`opencode`、`antigravity`或`pi`之一； `<fixed-route>` 是步骤 1 表中已批准的具体路线标记（`codex`、`claude`、`grok-cli`、`grok-cursor`、`cursor`、`composer`、`opencode`、`antigravity` 或 `pi`）。
- `<base-ref>` = 第 1 阶段 `BASE`（差异基于通过 `git diff <base-ref>` 进行的同行评审）。
- `<run-dir>` = 第 4 阶段的绝对运行目录。该脚本**仅在**将 `reviewer` 强制为 `adversarial-<provider>` 并将对等点 `safe_auto` → `gated_auto` 降级之后才在此处写入 `adversarial-<provider>.json`。

每个持久的作业 ID 仍然是生命周期义务，直到其工作人员终止并且其作业目录在技能返回之前被删除。正常的审查路径通过单次收割完成和下面的折叠来满足该义务。如果本地工作流无法继续折叠，则立即收割对等点，执行最后的`wait --max-secs 10`，因为收割是异步的，并删除其作业目录，而不读取或折叠结果或尝试路由恢复。

**单次收割完成。** 跑步者将工作人员分离到其自己的监督会话中。 捕获 `start` (`date +%s`) 之后的纪元时间，并且在本地审查者处于活动状态时不要进行轮询。 收集本地退货后，检查一次状态。 如果作业仍在运行，则发出有界 `wait` 切片，直到作业终止 **或** 自 `start` 以来，共享截止日期（来自 `start` 调用的 `peer-deadline-secs`；默认为 1210 秒）已过去。 将 `date +%s` 与每个切片之前捕获的开始时间进行比较，并且永远不要开始超出截止时间的切片。 将每个切片的大小调整为最多 480 秒（Luna xhigh 运行可以合法地花费约 419 秒，因此较短的切片可以在健康对等点返回之前结束），并让切片重复：一个切片远短于派生的截止日期，因此限制*总*等待将收获一个健康的对等点，这正是扩大预算的原因。 切片不是轮询轮次。 不要在切片之间交错状态读取、shell 无操作或“仍在等待”轮次。 当工作结束时折叠产物。 在截止日期时，`reap <job-id>` 并执行最后一次`wait --max-secs 10`，因为收获是异步的。 该脚本限制了自己的运行时间（空闲超时 480 秒；硬逆止`CROSS_MODEL_HARD_SECS`，默认 1200 秒）*在*该截止日期内，因此在截止日期内收获是例外。 完成是通过文件的存在来检测的：工作人员仅在标准化后发布`<run-dir>/adversarial-<provider>.json`。 该脚本从技能目录中读取角色简介和模式，并根据 `<base-ref>` 检查当前工作树。 它的大差异预检仅用于传输：它测量精确的差异并将其放置在提示之外；编排者选择语义划分，审查者选择其中的代表和证据。

`start`返回的作业ID就是启动成功的证明。不要立即致电`status`、检查`--help`或以其他方式进行验证；坚持下去，继续本地调度。状态收集仅在本地波形完成后开始。

本参考中的命令是可执行合约。在调度之前，请勿检查或 grep 工作脚本的模型映射或白名单、运行 `CROSS_MODEL_DRY_RUN`、调用 `--emit-adapter` 或探测运行程序 `--help`。这些探索性呼叫只会重播主机上下文，无法加强跑步者执行的路线。

本地审查者完成后，读取的状态如下：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/peer-job-runner.py" status "<job-id>" --json
```

如果它仍在运行并且时间剩余，则每个 `wait` 切片恰好是：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/peer-job-runner.py" wait --max-secs <remaining-slice-secs> --json "<job-id>"
```

重复该调用，直到作业结束或派生的截止日期已过；不要发明备用状态标志或检查帮助。

## 第 5 步 — 折叠到第 5 阶段

- 通过运行器的验证读取来读取产物（在同一工具调用中解析 `$PY` - shell 不会持久）：

  ```bash
  SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
  PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
  "$PY" "$SKILL_DIR/scripts/peer-job-runner.py" result "<job-id>" --path <run-dir>/adversarial-<target>.json
  ```

  运行程序检查它是否拥有文件描述符并限制读取。出口 0 发出产物。 Exit 2表示作业仍在运行，因此上面的截止日期循环提前离开了；返回它而不是分类。 Exit 3 是唯一的结果，意味着对等点没有产生任何结果；它命名了作业的状态，然后读取 `references/cross-model-recovery.md` 并遵循与该状态匹配的分支，因为它独自拥有当对等点没有产生可用产物时发生的情况。任何其他退出都意味着运行程序无法完成读取：产物或作业自身状态的信任失败，或者作业 ID 无法解析。这些都没有恢复分支。将 Coverage 中的失败命名为降级的跨模型传递，并且切勿将其折叠到干净的跳过中。

  其结果进入普通重复数据删除，但仅当`independence_verified`为`true`**时才允许协议升级。错误或缺失的值可能有助于发现结果，但永远不会提高信心。 `independence_verified` 证明了一个不同的服务家庭；它没有声称确切的服务模型已得到验证。 `receipt_supported`、`model_actual`和`effort_actual`携带单独的身份证据。同行的研究结果永远不会授予默默应用的权力。
- 在最终的 Coverage 中，命名产物中的 `cross_model_route`、`model_requested`、`effort_requested`、`receipt_supported`、`model_actual`、`effort_actual` 和 `independence_verified`。保留字面值`unverified`；当实际模型或工作未经验证时，切勿将请求压缩为服务声明，例如“via Codex high”。上述披露条件决定了同行在报告中的命名方式。
- **从未启动/未运行** - 作业从未启动（未满足运行条件、被签出配置禁用、主机不可证明、未安装不同提供商路由或 CLI 缺失）：通行证根本没有运行。请注意面向人的Markdown覆盖范围中的“跨模型传递：未运行”，或者当步骤 1 的结帐策略是原因时，“跨模型传递：由结帐配置禁用”。在`mode:agent`中，不宣布跳过； JSON结果将其记录为`references/modes-and-output.md`定义。忽略任何 `*.raw.json` 剩下的东西——它们不是折叠式的文物。
- 空`findings`→注意Coverage中的“cross-model pass: no extra issues”。
- 折叠后（或截止时间收获后），删除消耗的作业目录（`<run-dir>/jobs/<job-id>/`）。其日志和结果是审查内容，不得超过其使用期限。
- 仅当产物记录 `independence_verified: true` 时，与进程内 `adversarial` 共享指纹的发现才会升级。光标默认产物默认 false；未经认证的主机会跳过自动调度。
