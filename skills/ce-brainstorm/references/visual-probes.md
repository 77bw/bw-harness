# 视觉探头

当通过看到粗糙的产物比阅读散文更快地做出头脑风暴决策时，请使用视觉探针。视觉探针是一次性决策草图，而不是原型、实施计划、UI 规范或设计交付成果。

## 扳机

仅当下一个问题具有特定的视觉决策时才使用此参考：

- 行为形状：“哪种注释或绘图行为感觉正确？”
- 布局形状：“哪种导航结构与工作流程匹配？”
- 流程形状：“这个决策点应该放在哪里？”
- 状态形状：“哪个empty/loading/error状态传达了正确的信息？”
- 图表形状：“哪种关系或系统边界更清晰？”

不要将视觉探针用于产品目标、范围边界、成功标准、证据探针、权衡散文或更容易在聊天中讨论的技术决策。满足 `references/interaction-rules.md` 中交互规则 7 的决策（规定测试）属于 `ce-prototype`，而不属于视觉探针。

**对广泛的决策进行分类。** 仅在命名途径后，才适用按途径分类。未分解的决策根据其主导维度进行一次分类。当任何命名的大道满足规则 7 时，整个决策将转向`ce-prototype`——可绘制的大道作为薄变体沿着那里行驶，而不是将一个决策分成两层。

## 大门（当报价必须触发时）

当阶段 0.3 标记了一个固有视觉主题时，必须在以“任何”形式（普通聊天或阻塞问题）提出有关形状、行为、状态、布局、流程或图表的“第一个”决定之前提出要约。满足交互规则 7 的决策改为路由至`ce-prototype`；这条规则不适用于它。

**时间是基于状态的，而不是基于内存的。** 将检查锚定到您将要提出的决策，而不是锚定到自阶段 0.3 以来记住的“待定报价”：报价，除非此特定决策已经通过报价（用户已经为其选择了文本或视觉效果）。此规则优先于默认的阻塞问题路径 - 不要将形状决策作为阻塞问题菜单或普通聊天形状问题提出，直到用户拒绝视觉（或视觉反馈返回到聊天）。

**完成报价后，仅关闭此报价，而不会关闭规则 7。 ** 两条路径重新打开此处已提供的决策的原型路线：用户选择文本，然后决策打开完成或动作，或者构建了一个粗略的草图，但没有解决它。将这些路由到`ce-prototype`，而不是将决策视为已结束。

**问题选项中嵌入的 ASCII 预览或文本模型不能满足要约** — 该快捷方式正是此规则所要阻止的。该报价是它自己的先决问题，有两个选项（草图与描述）；只有在用户选择之后，形状决策才会继续。

## 提供

在决策点询问一次。不要启用会话范围模式。

使用当前工具列表中已有的主机阻止问题工具（按功能匹配，而不是按主机特定名称匹配）。当前工具列表中的存在证明该工具存在；永远不要调用面向用户的提问工具来发现它是否存在。如果列出了匹配的工具但已卸载，请使用主机的工具发现原语来加载该功能 - 不要搜索另一个主机的工具名称。仅当列表中没有此类工具或实际问题调用错误时才使用普通聊天问题。选择加入应该有两个明确的选项：

- 视觉草图——在本地浏览器中创建粗略的选项
- 文字描述——在聊天中保留决定

使用这样的措辞：

> 这个决定可能更容易通过视觉来判断。我可以在本地浏览器中绘制粗略的选项，以便您可以对形状做出反应，或者将其保留在聊天中并以文本方式描述选项，这更快但保真度较低。你更喜欢哪一个？

文本路径必须是可信的。如果你不能用文字清楚地解释这个决定，那么你就没有充分理解它，无法勾勒出它。

如果用户选择文本，请继续聊天，并且不要再次提出相同的决定。如果他们选择视觉，请继续以下操作。

## 视觉路径

创建回答当前问题的最便宜的产物。优化是为了快速反馈，而不是润色。

允许：

- 粗略的行为草图
- 低保真线框
- 状态比较
- 流程图
- 简单的A/B/C视觉对比
- 仅当单一行为形状是决策时才使用一次性单决策交互演示 - 不是大范围的、分层的切片或应用内覆盖

避免：

- 抛光品牌
- 最终颜色或版式
- 元件库精度
- 像素完美的布局
- 类似生产的实现
- 不必要的动画
- 暗示确切 UI 承诺的细节

将产物标记为定向。说明用户应该判断什么以及应该忽略什么。

## 显示助手

当当前平台可以运行捆绑的技能脚本时，使用捆绑的仅显示帮助程序。通过 `SKILL_DIR` 锚点调用它：将 `SKILL_DIR` 设置为包含您加载的 `ce-brainstorm` `SKILL.md` 的目录的绝对路径（Bash 工具的 cwd 是用户的项目，而不是技能目录），并在每次调用时在同一命令中重新设置它，因为 shell 变量在 Bash 调用之间不会保留。不要从用户的项目 CWD 解析帮助程序。

开始（分离）：

```bash
SKILL_DIR="<absolute path of the ce-brainstorm skill directory>";
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
PROBE_DIR="$SCRATCH_ROOT/ce-brainstorm-visual/<run-id>"; (umask 077; mkdir -p "$PROBE_DIR") || exit 1; chmod 700 "$PROBE_DIR" || exit 1;
node "$SKILL_DIR/scripts/light-webserver.js" start --root "$PROBE_DIR"
```

将 `--foreground` 附加到 `start` 命令以实现前台模式。 Status 和 stop 采用相同的锚点 - 并且由于 `SKILL_DIR` 在 Bash 调用之间不会持续存在，因此每个调用都必须在自己的调用中重新设置它，而不是重用 `start` 块的值：

```bash
SKILL_DIR="<absolute path of the ce-brainstorm skill directory>";
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
PROBE_DIR="$SCRATCH_ROOT/ce-brainstorm-visual/<run-id>"; (umask 077; mkdir -p "$PROBE_DIR") || exit 1; chmod 700 "$PROBE_DIR" || exit 1;
node "$SKILL_DIR/scripts/light-webserver.js" status --root "$PROBE_DIR"
# stop: the same command with `stop` in place of `status` (re-set SKILL_DIR again)
```

如果`SKILL_DIR`无法解析为具体的技能目录，请不要从项目CWD中猜测——使用文本路径。

帮助器创建`screens/`和`state/`，提供`screens/`中最新的`.html`文件，写入`state/display-info.json`，并公开`/version`，以便浏览器可以轮询屏幕更改。仅当最新屏幕发生变化时，浏览器才会重新加载；它不能不断地重新加载计时器。 `/version` 轮询不算作活动，因此废弃的浏览器选项卡无法使服务器永远保持活动状态。分离的服务器会在可以解决问题时监视所属的宿主进程，并且所有服务器会在空闲超时后退出。该帮助程序没有点击跟踪或浏览器到代理的事件路径。

如果辅助路径不可用或者平台无法清晰地显示本地 URL，请简单说明并使用文本路径。不要构建自定义事件系统或长期服务器来在头脑风暴期间进行补偿。

## 按平台划分的启动模式

服务器到处都是一样的；仅启动模式发生变化。

- **Claude Code / Claude 桌面应用程序：** 分离的 `start` 是默认路径。如果应用程序打开本地主机 URL，则显示返回的 URL 并继续。如果浏览器界面不可用，请使用文本路径。
- **Codex CLI / Codex app：** 如果在工具调用后分离进程被回收或 URL 消失，则通过平台的 long-running/background 终端机制使用 `start --foreground`。如果没有稳定的浏览器表面，请使用文本路径。
- **普通终端UI：**打印返回的URL供用户手动打开。如果打开浏览器会中断流程，请在聊天中做出决定。
- **远程或容器化会话：** 如果从用户的浏览器无法访问 `localhost`，则从 `--host 0.0.0.0` 开始并告诉用户要打开哪个 host/port。它将运行目录提供给任何可以到达端口的东西，无需身份验证 - 仅在用户信任的网络上执行此操作，并在您交出 URL 时说明这一点。如果无法明确，请使用文本路径。

切勿强制使用可视路径，因为存在本地服务器。用户选择视觉是为了更快地理解决策；如果平台管道妨碍，请切换回文本。

## 产物后反馈

显示视觉产物后，使用当前工具列表中已有的主持人阻塞问题工具来获取有界产物反馈。这仍然是基于聊天的反馈，而不是浏览器事件捕获。

当预期响应是一个小的选择集时，使用有界交互式问题：

- A/B/C/D 选项选择
- 视觉方向与组合
- 选择一项layout/state/behavior
- 接受一项带有请求调整的选项

当工具支持时，包括自由文本后备选项。仅当反馈是真正公开的批评、不存在交互式问题工具或工具错误时才使用普通聊天。

好的神器后提示：

> 哪个方向最符合您的需求？选择 A、B、C、D 或混合，并使用自由文本后备来处理任何感觉不舒服的情况。判断行为形状，而不是确切的样式。

不要要求用户在浏览器产物内单击。问题工具用于产物可见后的 chat/session 响应。

## 互动合约

browser/artifact 仅用于显示。反馈发生在聊天中。

不要在 v1 中添加点击跟踪、选定状态、事件摄取、表单、分析或“提交”功能可见性。不要要求用户单击选项。请他们查看产物并在聊天中回复选择、混合或更正。

如果没有可用的交互式问题工具，请在显示产物后使用此简单聊天后备：

> 我展示了三个粗略的选择。在这里回复 A、B、C 或“混合”，以及任何感觉不对劲的内容。判断行为形状，而不是确切的样式。

用户的聊天回复具有权威性。视觉产物仅支持上下文。

## 文件放置

默认情况下使用操作系统温度，因为视觉探针是一次性的划痕：

```text
<scratch-root>/ce-brainstorm-visual/<run-id>/
  screens/
    001-<decision>.html
  state/
    display-info.json
```

仅当用户明确想要在会话后检查、保留或整理草图时才使用 `.context/compound-engineering/ce-brainstorm-visual/<run-id>/`。探头为一次性划痕；持久产物是`<root>/plans/`下的第3阶段仅需求统一计划。
