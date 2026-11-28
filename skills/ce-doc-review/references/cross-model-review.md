# 跨模型判断通过

在只读、最低权限进程中通过一个单独路由的模型目标运行 ce-doc-review 的 **条件判断镜头**。每个同行都会获得与正在进行的审查者使用的**相同的**角色简介，返回相同的 `findings-schema.json` 形状，并折叠成与审查者 `<reviewer-name>-<provider>` 一样的合成。只有当其结果文件记录`independence_verified: true`时，才算独立佐证，才能促进一致；否则，它仍保留为评论证据，而没有晋升奖金。

这三者是三个**条件**判断镜头，其输出在模型系列中差异最大：`adversarial-document-reviewer`、`product-lens-reviewer`、`security-lens-reviewer`。会聚镜头（`coherence`、`scope-guardian`）和常亮 `feasibility` 镜头**不**跨模型运行。可行性被明确排除，因此通行证保持有条件，并且不会在每次审查时产生。

在任何文档内容离开机器之前，主机会解析并批准一条具体路由（本引用文档将其称为出口）。捆绑的 **`scripts/cross-model-doc-review.sh`** 强制执行固定路由，编写提示，应用最小权限，捕获模式形状的 JSON，并规范化它返回的模型身份记录。该传递是非阻塞的：失败的路由不会写入折叠产物，并且永远不会在内部切换接收者。

## 条件 — 仅当满足时才运行

仅当通过正常的第 1 阶段角色选择逻辑为此文档激活该镜头时**才对给定的三重镜头运行跨模型传递。没有引入新的激活触发器：具有经过验证的上游来源且没有高风险域的例行计划不会激活这三者中的任何一个，因此它不会获得跨模型传递。第一阶段的缺失文档检查已经保证了文档在磁盘上可读。没有差异，也没有远程范围问题，因此不需要额外的范围检查。

## 第 1 步 — 证明主机身份，然后批准一条固定路由

保持四个独立的身份：请求的 **目标**、CLI **harness/intermediary**、服务 **family/provider** 和服务模型。 `cursor` 表示 `cursor-agent` 及其配置的 default/Auto 模型，因此没有 `--model` 标志。 `composer` 表示通过 `cursor-agent` 的显式 Composer 系列模型。 `grok`更喜欢原生Grok CLI；尽管请求的目标仍然是 Grok，但通过 Cursor 的 Grok 是不同的路线和接收者。 `antigravity` 表示通过 Google 的 Antigravity ACP 运行时构建的 Gemini 模型；对 Gemini 对等点的请求绑定目标 `antigravity`。 `pi` 表示 Pi 编码代理在其自己配置的模型上，除非 `provider/model` 引脚指定了一个； Pi 为任何提供者提供服务，因此 `pi` 同级的服务家庭是未知的，并且其审查从来都不是独立的。

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

将`XHOST_HARNESS`传递为`CROSS_MODEL_HOST_HARNESS`；传递 `XHOST_FAMILY` 作为第一个工作参数。该片段是证据，而不是结论：它解析了其环境标记已命名的宿主，并且在您可以从自己的运行时识别的宿主上产生`unknown`，证明您所知道的。代码片段未命名的宿主此处不需要新分支。这两个令牌都来自工作人员接受的对等密钥词汇，而不是提供商的公司名称：家族`codex`、`claude`、`grok`、`composer`、`gemini`或`unknown`；宿主 `codex`、`claude`、`grok`、`cursor`、`opencode`、`antigravity`、`omp`、`pi` 或 `unknown`。任一插槽中的诸如 `anthropic`、`openai` 或 `xai` 之类的名称都会使工作进程停止而不会出现任何产物。

Claude Code、Codex 和 Grok 各自服务于自己的模型系列，因此当该宿主的标记是唯一存在的此类标记时，该片段会从该系列中获取该系列。另一个宿主可以复制这些标记之一（oh-my-pi 设置 `CLAUDECODE=1` 无论模型为其提供服务），并且从另一个宿主内部启动的会话会继承该宿主的标记。因此，该片段将家庭 `unknown` 留在为任何模型（oh-my-pi 或 Pi）提供服务的宿主上，或者当存在多个标记时。将片段名称传递给家人。在它离开系列 `unknown` 的地方，仅从运行时发布的模型 ID 设置它作为服务于该会话的模型，并且仅当该 ID 映射到`codex`、`claude`、`grok`、`composer` 或`gemini` 时。请求的型号、该型号自己的声明以及产品名称都不是该 ID。切勿从 Cursor 品牌推断服务家庭。未知的宿主族无法满足自动同族排除，因此跳过自动跨模型传递。

当代码片段产生harness `omp`或`pi`时，此跳过尚不适用：仍然传递`unknown`并开始作业。工作人员从利用会话记录的模型中读取服务族，并在没有指定第一方模型时跳过。

<!-- ce-config-layers:start -->
**解析两个存储库文件中的普通 CE yaml 密钥。**

- **读取** `<repo-root>/.compound-engineering/config.local.yaml`，然后读取 `config.yaml` (`<repo-root>` = `git rev-parse --show-toplevel`)。丢失的文件将被跳过。 Gitignore 不会改变分辨率。
- **以第一个活动（未注释）值获胜**。对于标量，未设置空；无效值继续下一层，则技能默认。对于列表和地图，现有的键（包括空列表或地图）将替换整个键。
- **不要**将此规则用于 `docs_root` — 该键仅是 `config.yaml`。
<!-- ce-config-layers:end -->

**检查出口策略 - 首先评估这一点。** 在普通密钥规则下从相同的两个存储库 CE 配置文件中读取 `cross_model_review_mode:`。有效值为`auto`（默认）和`off`；其他任何内容都无效并继续到下一层，然后是`auto`。当它解析为`off`时，在对等解析、披露或任何作业开始之前，跳过此处的自动跨模型传递，除非用户在对话中明确要求跨模型对等运行（`cross_model_peer`值或项目指令首选项不是选择加入）。将跳过原因记录为**由签出配置禁用**，与不可证明的主机或不可用或非独立的路由不同；每个三镜头都保持其进程中的双胞胎，就像任何从未启动的同级一样，并且整个文档扫描不会运行。实时用户禁止仍然优先于 `auto`。

按此顺序解决首选项：

1. 用户**在对话中陈述**的偏好（例如“使用 grok 进行跨模型传递”）。
2. `cross_model_peer:` 来自两个 repo CE 配置文件（`config.local.yaml` 然后`config.yaml`）。应用普通键规则：第一个主动支持的目标获胜；无效值继续到下一层，然后是步骤 3。
3. 您的**项目说明**（您的上下文中的活动说明）中已有的首选项，取自上下文并且**从不**从命名文件中读取。
4. **默认值：** `codex → claude → grok → antigravity` 中第一个可用的已证明不同目标。 Cursor default 和 Composer 仅在步骤 1-3 之一命名时运行。

在发送任何内容之前，将每个选定的目标解析为一个具体的已安装路由，公布它，并将其作为`CROSS_MODEL_FIXED_ROUTE`传递。 `CROSS_MODEL_PEERS`是可选的出口限制，而不是必需的批准：设置后，每个收件人（目标和中间人）都必须根据下面的别名规则受到其批准，未经批准的收件人是指定的跳过；当它未设置或为空时，不会过滤任何收件人并继续传递。在这种情况下，该技能调用加上出口前披露就是制裁（在非交互模式下，调用技能的请求就是该制裁，而 stderr 审核日志就是披露）。不要检查工人来源来重新发现这一点；它完全执行了这个合同。 `CROSS_MODEL_FIXED_ROUTE` 完全接受这些标记；工作人员在其他任何事情上都会停下来（包括像`codex-cli`这样的路线形状的猜测）：

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

失败的调度路由不会返回任何产物；它永远不会在内部改变提供者或中介。重试同一已解决的路线将保留其现有的制裁和披露；更改路线或任何收件人需要新的决议、制裁和交付前的披露。只有在路由适配器报告提供者过载（HTTP 529）作为提示错误类型`overloaded`之后，工作人员才可以重复相同的路由一次；它使接收者、模型、范围和共享对等截止日期保持固定。今天只有克劳德适配器报告了这种形式；其他适配器在内部重试重载，因此从它们到达工作线程的过载会以普通故障结束。为了向后兼容，`CROSS_MODEL_PEERS`中的`cursor`或`composer`都认可Cursor作为中介，但选择Cursor默认语音本身需要目标`cursor`； `grok` 永远不会单独制裁 Grok-via-Cursor。反重力路线仅受字面`antigravity`认可； `CROSS_MODEL_PEERS`中的`gemini`什么也不承认。

**签出配置的模型和工作。**解析目标后，在普通密钥规则下从相同的两个存储库CE配置文件中读取`cross_model_model:`和`cross_model_effort:`。当`cross_model_model`设置时，传递`CROSS_MODEL_MODEL_OVERRIDE_TARGET=<resolved-target>`和`CROSS_MODEL_MODEL_OVERRIDE=<value>`；当`cross_model_effort`设置时，传递`CROSS_MODEL_EFFORT_OVERRIDE=<value>`。两者都使用下面启动调用的 `env` 前缀。工作人员根据实际运行的路线验证每条路线。模型必须是已解析目标自己的系列（别名，例如 `fable` 或完整 ID，例如 `claude-opus-5-5` 代表 `claude`；`gpt-*` 代表 `codex`，可选命名空间限定，例如 `openai.gpt-6.1-sol`，当 CLI 通过非默认 `model_provider` 路由时； `gemini-*`为`antigravity`；`provider/model`为`opencode`和`pi`）；努力必须是路线适配器提供的级别，对于`antigravity`来说是它的思维级别，`low`，`medium`或`high`，对于`opencode`（2.x）是`none`到`max`，如模型列出的那样；光标代理和`pi`路线不接受任何努力覆盖。不兼容的值会以指定的跳过原因停止传递，而不是进行替换。取消设置键会使脚本的编辑映射保持不变。完全按照要求在步骤 3 行中公布配置的模型和工作量。用户在对话中陈述的模型或工作比配置键更重要。

首先运行首选模型映射。只有在观察到首选 ID 不可用、过时或不兼容后，主机才可以检查当前的 CLI 功能并选择最接近的兼容 **same-target/same-family** 替换。将其与`CROSS_MODEL_MODEL_OVERRIDE_TARGET=<target>`和`CROSS_MODEL_MODEL_OVERRIDE=<model-id>`绑定。切勿跨系列替换、将一个目标的覆盖应用到另一条路线、默默地更改显式模型或添加收件人。

目标`antigravity`从不接受主机选择的替换。其工作人员请求 Gemini 4 Argon，当账户不提供 Argon 时，会在发送任何提示之前退回到 Gemini Flash；运行日志命名所使用的模型。配置的 `antigravity` 模型完全运行，否则过程会跳过。

法典工作人员以同样的方式对待自己的编辑请求。当帐户不提供默认模型时，它会在发送任何提示之前回退到备用模型。当适配器拒绝编辑推理工作时，它会在没有编辑推理的情况下重试一次并记录`effort_requested: unverified`。配置的 Codex 模型或工作会完全运行，否则会跳过传递。

## 第 2 步 — 提供者模型 + 推理层（在脚本中定义）

所有激活的镜头都在**每个提供商的一个型号上以高推理运行，除了原生 Grok 在超高推理上**。光标代理 Grok 路线使用 Cursor 的 high/fast 预设，因为 Cursor 为每个模型提供一个预设；作曲家的快速层是其上限，这是一个公认的例外。具体模型 ID 和每条路由推理标志位于脚本中的 **单个映射**（`scripts/cross-model-doc-review.sh`、`M_CODEX`/`M_CLAUDE`/`M_GROK`/`M_GROK_CURSOR`/`M_COMPOSER`/`M_ANTIGRAVITY` 常量和`adapter_argv` 构建器）。结帐可以通过 `cross_model_model` / `cross_model_effort` 固定已解决目标的模型和工作（步骤 1）；该脚本会验证并且不会替代。此引用文档故意**不**重述 ID；事实来源之一可以防止引用文档和脚本发生偏差。 ID 是层规则（单个维护点）下的当前选择，而不是合同。

**角色文件**基本名称和 **审查者名称**是不同的：脚本从 `references/personas/<persona-file>.md` 读取摘要，但强制将 `reviewer` 字段折叠到 `<reviewer-name>-<provider>`，以便协议与进程内角色的短名称相匹配。该脚本从列入白名单的审查者姓名派生角色文件。它不是调用者参数，因此没有调用者值到达简短读取路径。

## 第 3 步 — 宣布

预调度资格基于已安装的路线存在和制裁，而不是凭证状态。在提供程序支持的启动之前不要运行身份验证探测；只有在提供者能够调度之后，身份验证才是权威的。

- **交互式主机，默认交互模式：**显示一条**突出的独立线**，将其框架为判断镜头的**独立跨模型审查**（说“跨模型”/“独立模型”，而不是内部“同行”行话）。该行根据脚本内映射命名具体的**模型和推理级别**（例如，高推理的 GPT-6.1 Sol、高推理的 Opus、超高推理的 Grok 4.7、快速的 Composer 2.5）。因为两个不同的模型可以通过 *相同* `cursor-agent` CLI 到达，所以它为游标代理路由命名**路由和模型**，因此 Grok-4.7-via-cursor-agent、Composer-via-cursor-agent 和 Grok-4.7-via-the-grok-CLI 是明确的。 **它声明完整的文档内容将发送到该提供商**（第三方出口；对于游标代理路由，内容将发送到游标*加上*服务提供商）。 **一个披露条件控制着公告以及以后每次提及对等点：** 按目标和请求的模型将其命名为请求（“请求的 <model>”），而不是作为该模型服务的声明。仅当服务模型记录与请求不一致或路由请求无模型时（光标 default/Auto 表示“服务模型未验证”），才添加服务警告。具有所请求型号的无收据路线不会有任何警告：`model_actual: unverified` 表示没有记录，而不是未知型号。将其与第二阶段团队公告一起放置，而不是埋在其后。措辞是你的；可检查的要求是：突出，读取为**跨模型审查者**（不是通用角色），根据请求命名请求的模型，在光标代理时命名路线，命名出口。示例：`🔀 Cross-model pass — the judgment lenses are also being reviewed by an independent model: requested **Grok 4.7 (high reasoning), via cursor-agent**. Full document content is sent to xAI/Cursor.`
  - 仅当寄宿家庭和目标服务家庭明显不同时，才将通行证称为“独立”。对于光标default/Auto或未知的寄宿家庭，称其为跨线审查，并声明独立性未经验证；在服务模型记录存在之前，不要承诺协议升级。
  - 交付前公布一条固定路线及每位收件人。路由失败不会产生任何产物；在再次尝试之前应用步骤 1 的 retry/disclosure 条件。协调产物中的 `cross_model_target`、`cross_model_harness`、`cross_model_route`、`model_requested` 和 `model_actual`；切勿从请求的 ID 推断服务模型。上述披露条件决定了同行在报告中的命名方式。
- **交互式主机，没有对等点解析**（主机不可证明，没有安装不同提供商的路由，或通过结帐配置禁用）：跳过跨模型传递的一条安静线路以及原因；如果这是原因，请指定结账政策。从来没有错误。
- **非交互模式：**不宣布通行证。该脚本仍然会在每次发送文档内容跨模型发送到指定提供程序时发出一行 stderr 审核日志，因此即使传递未向用户公布，第三方数据出口也是可审核的。非交互式应用与交互式相同的条件：已安装、已批准、已证明的不同路线在第 1 步合同下运行，包括未设置的许可名单。当激活三重镜头时，结构化结果仍然记录对等产物是否被折叠，以`references/synthesis-and-presentation.md`定义的形式。

## 第 4 步 — 运行捆绑脚本（每个激活的三重镜头一次调用，与角色审查者并行）

每个呼叫都是 CLI 的 shell-out，而不是子代理。每次文件审查时解决一个目标和一条固定路线，然后针对同一批准的target/route启动每个激活的镜头。通过 `scripts/peer-job-runner.py` 在与正在进行的审核者相同的调度波中将每个呼叫作为独立作业启动。失败的路线不会在工作人员内部通过。

**两种模式 - 切片三重奏，扫描整个文档：**

- **三重对等，切片。**在**统一产物**上，将*其进程中双胞胎得到的*相同审查者特定切片*传递为`<document-path>`（将该切片写入临时文件 - 例如product-lens/adversarial获取产品合同），而不是完整文档，因此对等是真正的证实双胞胎而不是镜头外审查者。在遗留文档中，对等方获得与双胞胎相同的完整文档。
- **一次完整文档扫描。**在**同一波**中，还启动**一个**调用，其中审查者姓名**`whole-doc`**、**完整**文档（从未切片）和相同的已解析提供程序 - 对整个文档进行广泛的不同模型读取。它每文档运行一次（不是每个镜头），写入 `whole-doc-<provider>.json`，并作为独立审查者折叠起来，证实 *任何* 进程中的发现 3.3 与其合并（它没有进程中的双胞胎）。与三人组调用相同的门、隔离和非阻塞规则。每当通行证运行时，遵循此合同的模型必须发出此 `whole-doc` 调用，否则扫描所提供的广泛覆盖范围将被默默地跳过。

通过技能目录锚点调用 - 将 `SKILL_DIR` 设置为 **此** 技能的 `SKILL.md` 的绝对目录（Bash 工具的 CWD 是用户的项目，而不是每个主机上的技能目录；shell 状态在 Bash 调用之间不会持续存在，因此在每个运行程序调用中将其内联设置）：

**解释器。** 下面的命令运行捆绑的 Python 脚本。在与命令相同的 shell 调用中解析解释器——每个工具调用都是一个新的 shell，因此早期调用中设置的 `$PY` 不会持续存在。不要硬编码 `python3`：在本机 Windows 上，它解析为在不运行 Python 的情况下退出的 Microsoft Store 存根，并且该存根仍然满足 `command -v`，因此探测执行而不是存在。

```bash
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
```

**主机命令沙箱边界。** 分离的工作线程继承启动它的 `start` 调用的权限上下文。在执行该确切调用之前，将 `CODEX_SANDBOX_NETWORK_DISABLED` 视为当前 Codex 命令沙箱无法到达提供者的肯定信号；取消设置不会更改沙箱策略。仅 DNS 或身份验证失败并不能证明该情况。使用最窄的主机权限来恢复固定路由的提供商连接。当 Codex 仅公开完整命令升级时，请将此请求附加到现有出口公开后的确切 `peer-job-runner.py start ...` 工具调用：

```json
{
  "sandbox_permissions": "require_escalated",
  "justification": "Allow the disclosed read-only cross-model review to send the reviewed document to the fixed external provider."
}
```

透露这不是仅限启动器的隔离：分离的工作程序在其生命周期内继承该启动上下文，因此适配器声明的 read-only/tool 限制（而不是 Codex 命令沙箱）在审查的材料流出时绑定对等点。如果授权被拒绝或不可用，则不执行`start`；不创建同行工作并保留正在进行的评审员作为覆盖范围。在 `start` 返回作业 ID 后，任何网络、身份验证或提供程序故障都是开始作业结果，并遵循普通的 terminal/recovery 规则；将 `status`、`wait`、`result` 和 `reap` 保留在沙箱中，因为它们不需要提供者连接。

```bash
SKILL_DIR="<absolute path of the directory containing the ce-doc-review SKILL.md you read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
RUN_DIR="$SCRATCH_ROOT/ce-doc-review/<run-id>"; (umask 077; mkdir -p "$RUN_DIR") || exit 1; chmod 700 "$RUN_DIR" || exit 1;
echo "peer-deadline-secs=$(( ${CROSS_MODEL_HARD_SECS:-1200} + 10 ))";
CE_PEER_HARD_SECS= CROSS_MODEL_HOST_HARNESS="<host-harness>" CROSS_MODEL_FIXED_ROUTE="<fixed-route>" "$PY" "$SKILL_DIR/scripts/peer-job-runner.py" start --skill ce-doc-review --run-id "<run-id>" --label "<reviewer-name>" -- env CROSS_MODEL_HOST_HARNESS="<host-harness>" CROSS_MODEL_FIXED_ROUTE="<fixed-route>" bash "$SKILL_DIR/scripts/cross-model-doc-review.sh" "<host-serving-family>" "<target>" "<reviewer-name>" "<document-path>" "<document-type>" "<origin>" "$RUN_DIR"
```

当步骤 1 解析配置的模型或工作时，将 `CROSS_MODEL_MODEL_OVERRIDE_TARGET="<target>" CROSS_MODEL_MODEL_OVERRIDE="<model>"` and/or `CROSS_MODEL_EFFORT_OVERRIDE="<effort>"` 添加到 `CROSS_MODEL_FIXED_ROUTE` 之后的 `env` 前缀；未设置时忽略它们。

嵌套窗口是一个预算，一个旋钮，`CROSS_MODEL_HARD_SECS`。跑步者自动从环境旋钮（`max(1230, knob + 30)`）获取其监控硬窗口。清除起始前缀 (`CE_PEER_HARD_SECS=`) 上的 `CE_PEER_HARD_SECS`，以便来自早期会话或宿主导出的陈旧环境值不会削弱该派生。当技能故意设置 1（ce-work / 海拔）时，显式数字 `CE_PEER_HARD_SECS` 仍然会获胜，而这条路径不能这样做。在与 `start` （如上所述）相同的 shell 中将协调器截止日期打印为 `knob + 10`，并使用下面打印的`peer-deadline-secs=<n>`（所有支路共享一个值；重复使用第一个支路的编号，而不是重新派生每个支路）；永远不要对它进行硬编码，因为文字在旋钮变化后仍然存在，然后获得健康的对等体。

**不要将`CROSS_MODEL_HARD_SECS`转发给worker。** runner已经通过了周围环境，因此用户实际设置的旋钮会自行到达worker。重新导出 Orchestrator 的“已解析”值会将回退转变为显式覆盖，并剥夺工作线程自身的默认值。

省略`--result-path`； `done`仅表示worker退出。固定目标决定了预期的 `<reviewer-name>-<target>.json` 文件名。

- `<host-serving-family>`是`codex`、`claude`、`grok`、`composer`、`gemini`或`unknown`； `<host-harness>` 为 `codex`、`claude`、`grok`、`cursor`、`opencode`、`antigravity`、`omp`、`pi` 或 `unknown`。
- `<target>`恰好是`codex`、`claude`、`grok`、`cursor`、`composer`、`opencode`、`antigravity`或`pi`之一； `<fixed-route>` 是步骤 1 表中已批准的具体路线标记（`codex`、`claude`、`grok-cli`、`grok-cursor`、`cursor`、`composer`、`opencode`、`antigravity` 或 `pi`）。
- `<reviewer-name>` = 激活的镜头（`security-lens`、`adversarial` 或 `product-lens`）。该脚本从该允许值中派生出人物简介文件名和（每个提供商）模型 - 简短路径永远不受调用者控制。
- `<document-path>` = 正在审核的文档。
- `<document-type>` = 第一阶段分类 (`requirements` / `plan` / `unified-requirements` / `unified-plan`)。
- `<origin>` = 进程内角色收到的相同`{origin_path}` 槽位。
- `<run-dir>` = 上面解析的绝对`$RUN_DIR`。该脚本**仅在**将 `reviewer` 强制为 `<reviewer-name>-<provider>` 并将对等点 `safe_auto` → `gated_auto` 降级之后，才在每个解析的对等点处写入 `<reviewer-name>-<provider>.json`。

每个运行程序调用都是有界的：任何工具调用都不会跨越任何主机上的工作程序运行时。在调度波之间，轮询未完成的作业（当监视的作业解决时，它会提前返回）：

```bash
SKILL_DIR="<absolute path of the directory containing the ce-doc-review SKILL.md you read>";
PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
"$PY" "$SKILL_DIR/scripts/peer-job-runner.py" wait --max-secs 30 --json <job-ids...>
```

捕获最终 `start` (`date +%s`) 之后的纪元时间。该时间戳是您知道截止日期何时过去的方式，因为没有其他任何东西可以跟踪工具调用之间的挂钟。在综合或任何返回之前，将每项开始的工作带到最终结果。虽然仍需要其结果，但循环有界 `wait` 调用，直到作业终止 ** 或自最终 `start`** 以来共享对等截止日期 (`peer-deadline-secs`) 已过。每次等待前将 `date +%s` 与该时间戳进行比较；不要开始等待，以免超过截止日期。收获不再需要其结果或截止日期已过的未完成作业，然后运行最后一次有界`wait --max-secs 10`传递（收获是异步的；终端记录在返回后有一个宽限期）。收集并分类第 5 步下每个已启动的作业。分离的脚本仍然自绑定（每条路线的空闲超时默认 480 秒；硬回溯`CROSS_MODEL_HARD_SECS` 默认 1200 秒）并干净退出；跑步者的监控窗口位于这些帽子之外，作为后挡板。该脚本不需要传入提示或模式 - 它从磁盘读取角色简介、`findings-schema.json` 和文档本身。

任何终止状态不是 `done` (`failed` / `timeout` / `died-without-result`) 的已启动作业均在 Coverage 行中以其镜头和终端状态命名（例如“跨模型安全镜头对等点：超时”）。一项工作在截止日期记录`timeout`收获，并在其原因中注明收获。预检失败永远不会产生作业 ID：真正的条件未满足跳过是`never-started`情况，但是在任何作业开始之前调度基础设施崩溃都不是干净的跳过，并会触发步骤 5 中的手动恢复规则。从未启动的传递不会获得已启动作业的终端状态行，也不会导致审核失败。在非交互模式下，结构化结果以`references/synthesis-and-presentation.md`定义的形式记录每个未折叠的欠镜头，无论其工作是否开始。丢失的折叠文件仍然是“该通行证没有针对该镜头运行”，绝不是审核失败，除非调度基础设施崩溃使整个通行证立即无效，第 5 步将其处理为所谓的整体通行证丢失（特别是整个文档广泛阅读），而不是每个镜头“未运行”。

跨模型传递**不会**收到进程中角色在第 2 轮以上获得的累积决策底漆；对等提示携带第 1 轮帧，无论轮次如何。这是经过深思熟虑的（跨模型在第一次时最有价值）。 Synthesis 自己的 R29/R30 抑制会捕获重新提出或已经解决的发现，因此重新提出前一轮被拒绝的发现的同行会在 Synthesis 时被丢弃（未显示）。

## 第 5 步 — 收集结果并清理

每项已启动的作业在返回前都必须收集并分类。仅当审查进行综合时，才将可用的发现纳入综合；不完整的审查报告了同行的成果，但没有应用调查结果。收集分类后，使用环境首选删除命令删除`<run-dir>/jobs`下消耗的作业目录。如果收集或清理无法完成，保留剩余证据并报告未解决的作业和阻塞项；永远不要声称它们已被清理干净。

- 通过运行程序的验证读取来读取每个折叠产物（在同一工具调用中解析 `$PY` - shell 不会持久）：

  ```bash
  SKILL_DIR="<absolute path of the directory containing the ce-doc-review SKILL.md you read>";
  PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
  "$PY" "$SKILL_DIR/scripts/peer-job-runner.py" result "<job-id>" --path <run-dir>/<reviewer-name>-<target>.json
  ```

  读取会检查文件所有权并受到限制。出口 0 发出产物。 Exit 2表示作业仍在运行，因此上面的截止日期循环提前离开了；返回它而不是分类。 Exit 3 是唯一的结果，意味着对等点没有产生任何结果；它命名了镜头的工作状态，它选择下面的匹配分支。任何其他退出都意味着运行程序无法完成读取：产物或作业自身状态的信任失败，或者作业 ID 无法解析。这些都没有以下分支：将覆盖率中的失败命名为降级的跨模型传递，并且永远不要将其折叠到干净的跳过中。如果存在，请将其视为一位审查者返回
- **没有文件，干净跳过**（在开始实际工作之前跳过脚本：主机不可证明，没有安装不同提供商的路由，CLI丢失，无法解析的输出，或镜头未激活）→通行证根本没有针对该镜头运行。请注意默认模式下交互式主机上的 Coverage 中的“cross-model pass：not run”，或者当步骤 1 的出口策略是原因时，“cross-model pass：disabled by checkout config”。非交互模式下，不宣布跳过；结构化结果将其记录为`references/synthesis-and-presentation.md`定义。未激活的镜头不是合格的通行证。决不让审核失败。忽略任何`*.raw.json`剩菜；它们不是折叠的文物。
- **调度基础设施故障与干净跳过。**上面的干净跳过是一个*选择*不开始实际工作的脚本。调度基础设施崩溃是不同的：运行程序或工作人员本身失败，通过任何作业开始之前的非零退出、preflight/detach失败或未解析的`$SKILL_DIR`/脚本路径。因为每条腿共享一个跑步者、路线和 `$SKILL_DIR`，所以这样的碰撞通常会立即掉落**整个**跨模型传递，而不是一个镜头。不要在第一个错误时将其折叠到干净的跳过中。手动重新运行**相同的已解析路由**，重新发出受影响的 `start` 调用，其中 target/model、空工作空间隔离和嵌入文档读取范围均保持固定。在审查仍然可以进行综合的同时执行此操作，每次失败都是新的且似乎可以恢复的失败，并且共享的同行截止日期有效。这是同路由重试，与下面的配额规则不同，后者需要新公开的路由。一旦失败重复发生或超过最后期限，就停止并放弃跨模型传递。每个三重镜头仍被其正在加工的双胞胎所覆盖；基础设施崩溃默默地取消了**整个文档的广泛阅读**（扫描腿没有双胞胎）加上跨模型验证。在“覆盖范围”行中将该损失命名为“未运行”，而不是让它消失。手动恢复可能无法替代不同的目标或提供者、将读取范围扩大到嵌入式文档之外，或者放松只读空划痕隔离。
- **出口前传输不可用。** 工作线路`transport unavailable (pre-egress, <scope>): <reason>`表示对等方未运行并且没有文档内容到达提供者；报告镜头不运行的原因。范围 `shared`（Node、`npx` 或 acpx 的 npm fetch）以同样的方式失败，因此没有其他路由可以替代它。范围 `route`（该路由的 CLI 丢失，acpx 配置文件替换了其启动命令，或者适配器拒绝了模型，并列出了可用模型）仅影响该路由。被拒绝的模型遵循下面的拒绝模型项；任何其他替换均遵循步骤 1 的新决议、制裁和披露规则。
- **已开始，但不是 `done`**（作业的最终状态为 `failed` / `timeout` / `died-without-result`） → 仍然是非阻塞的，但绝不会静默：根据步骤 4 的命名规则在 Coverage 中命名镜头和最终状态。
- **在删除作业目录之前对跳过原因进行分类。** 当对等点没有产生可用输出或以非`done`结束时，在清理之前读取其`out.log`，包括前缀为`peer skip evidence:`的有界行。具体命名观察到的配额、身份验证或功能故障。仅在启动上下文或提供者响应明确建立了提供者支持的调度后，才归因于帐户身份验证失败；然后报告观察到的故障和登录或凭据刷新修复。如果没有该证据，身份验证形状的对等文本仅描述对等点的执行上下文：沙盒主机可以产生与真正注销相同的信号，因此切勿将其报告为用户帐户正在注销或提示登录命令。跨模型传递是附加的，并且过程中的审查者仍然覆盖他们的镜头；获取它需要一个对等点CLI可以到达网络的上下文。在步骤1的精确过载条件下，worker独占一次同路由重试。除了下面的拒绝模型重启之外，一旦提供商无审核结果到达主机，主机就永远不会重新启动该对等点。在同一配额或使用限制证据在此会话中出现多次后，不要自动重试该路由；永远不要默默地继续向另一个收件人发送信息。
- **拒绝模型。** 请求的模型本身被拒绝：适配器未提供它，或者提供者为此帐户拒绝了它（`peer skip evidence (reply):` 携带提供者作为回复文本发送的拒绝）。只是模型失败了；该路线仍然可用。如果工作人员运行自己的默认模型（因为用户未配置或命名任何模型），请在同一路线上重新启动该镜头一次，而无需新的接收者。给它最接近的同族模型，当该行存在时从 `peer skip evidence (advertised models):` 中挑选，并按照步骤 1 的同族替换段落所述绑定它。每个受影响的镜头最多都会重新启动一次。覆盖率表明哪种模型被拒绝，用户可以将 `cross_model_model` 设置为有效的模型。配置的或用户命名的模型永远不会被交换。
- 空`findings`→注意Coverage中的“cross-model pass: no extra issues”。
- 仅当产物记录 `independence_verified: true` 时，3.3 与其进程内孪生 (`<reviewer-name>`) 合并才会提升一个锚定步骤。光标默认产物默认 false；未经认证的主机会跳过自动调度。两者是否描述一个问题是 3.3 的一次性测试，而不是章节或标题上的字符串匹配。

## 信任边界（维护者）

该脚本将 **完整文档内容** 嵌入对等提示中，并将其发送到外部模型提供商（OpenAI、Anthropic、xAI、Google 或 Cursor，具体取决于已解析的对等）。这是比仅进行差异审查更广泛的出口。 `CROSS_MODEL_PEERS` 限制哪些提供商可以接收内容。

每条路由都通过 acpx（代理客户端协议客户端）运行，它需要具有 `npx` 的 Node 22.13 或更高版本，以及路由自己的代理 CLI。第一次运行时，npm 会在支持的范围内获取符合条件的 acpx 版本；稍后运行重用缓存。对等点从空的对等工作区运行，没有项目上下文，也没有 MCP 服务器，并且 Claude 以安全模式启动，因此项目设置和挂钩不适用。 acpx 拒绝对等方发出的每个权限请求，并且每个适配器都以只读模式运行（其中有一个）。仅当代理在使用前请求许可时才会删除该工具，因此路由在对等方仍然可以执行的操作方面有所不同。

当要求在工作区外部读取文件并在其中写入文件时，路由分为两层。反重力读数尚未经过测试：

| 路线 | 在空工作区之外读取 | 未经许可仍可使用工具 |
|---|---|---|
| `claude` | 被拒绝 | 在空工作区中读取 |
| `grok-cli` | 拒绝 | 在空工作空间内读取； Web 获取和 Web 搜索，其 ACP 服务器无法禁用 |
| `opencode` | 被拒绝 | 在空工作区中读取（Web、编辑和子代理在其配置中被拒绝） |
| `codex` | **允许** | 读取任何地方和 shell 命令，包括写入：其适配器不强制执行只读模式 |
| `grok-cursor`, `cursor`, `composer` | **允许** | 随时随地阅读和搜索 |
| `pi` | 被拒绝（无需任何工具即可运行） | 没有任何。 Pi 没有请求许可，因此它的启动器会关闭其工具和 MCP；存储库的 Pi 设置、扩展和技能不会加载 |
| `antigravity` | 尚未测试 | 写入、编辑和 shell 请求被拒绝。它仅从其私人每次运行主页和空工作区加载技能和设置，而绝不会从用户自己的反重力或双子座设置中加载技能和设置 |

**接受的读取残留（codex + 游标代理路由）：** 两个适配器都无法通过 ACP 实现无工具化，因此它们的隔离性比 claude、grok-cli 和 opencode 路由弱。对于ce-doc-review自己的文档威胁模型来说，这是一个**可接受的**风险。所审查的文档是维护者自己的规划文档（低注入面），并且主机代理已经以比任何对等方更高的权限在回购中运行，因此可以读取主机已经读取的文件（并将其发送给文档已经发送到的提供者）的对等方不会增加任何实质性的新暴露。路线被保留而不是被拒绝；脚本的 stderr 审核日志记录每次发送，因此即使在非交互模式下，出口也是可审核的。
