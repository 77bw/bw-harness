# 预览助手

在提供本地 Web 原型时加载此内容。隔离的网络运行启动带有注释的助手； `references/annotation-loop.md` 拥有等待循环，当聊天时是后备。

该技能自带`scripts/light-webserver.js`。不要导入同级技能的副本——隔离禁止这样做。该文件是 Brainstorm 助手的字节相同的副本。

当当前平台可以运行捆绑的技能脚本时，请使用捆绑的帮助程序。通过 `SKILL_DIR` 锚点调用它：将 `SKILL_DIR` 设置为包含您加载的 `ce-prototype` `SKILL.md` 的目录的绝对路径（Bash 工具的 cwd 是用户的项目，而不是技能目录），并在每次调用时在同一命令中重新设置它，因为 shell 变量在 Bash 调用之间不会保留。不要从用户的项目 CWD 解析帮助程序。

在运行开始时解析一次问题目录，并为以后的每次调用重复使用它打印的绝对路径。不要根据命令重新派生它 - 服务器将其 pidfile 及其进程匹配为`--root`，因此以不同方式解析的启动和停止会留下孤立服务器。

运行时`RUN_SLUG`为`<date>-<short-question-slug>`；对于正在构建的问题，`QUESTION_SLUG` 是 `NN-<question-slug>`。涵盖第二个相关问题的运行解决了同一运行目录下的第二个问题目录。

在运行此块之前解决耐久性；它会读取两个决定一次，并且不会进行第二次读取。当用户要求不要将此运行留在存储库中时，设置`RUN_KEEP="no"`，并按原样运行该块 - 它将运行发送到 OS temp，并且没有其他任何更改。否则，当运行在 git 存储库内时，探测存储库根目录中的 `.context/compound-engineering/`；如果未覆盖，请提议将这一行附加到 repo-root `.gitignore`，仅在用户同意的情况下附加，并保留文件的其余部分。无论哪种方式，以操作系统温度为目标的运行都不会得到任何报价。

```bash
RUN_SLUG="<YYYY-MM-DD>-<run-slug>";
RUN_KEEP="yes";
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)";
TEMP_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$TEMP_ROOT" ] && (umask 077; mkdir -p "$TEMP_ROOT") 2>/dev/null && [ ! -L "$TEMP_ROOT" ] && [ -O "$TEMP_ROOT" ] && [ -w "$TEMP_ROOT" ] || TEMP_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ "$RUN_KEEP" = yes ] && [ -n "$REPO_ROOT" ] && [ ! -L "$REPO_ROOT/.context" ] && [ ! -L "$REPO_ROOT/.context/compound-engineering" ] && git -C "$REPO_ROOT" check-ignore -q .context/compound-engineering/ 2>/dev/null; then
ROOT="$REPO_ROOT/.context/compound-engineering";
else
ROOT="$TEMP_ROOT";
fi;
while :; do
BASE="$ROOT/ce-prototype";
if [ -L "$ROOT" ]; then echo "unsafe root symlink: $ROOT" >&2;
elif ! (umask 077; mkdir -p "$ROOT"); then echo "could not create $ROOT" >&2;
elif [ -L "$ROOT" ] || [ ! -O "$ROOT" ]; then echo "root is not owned by the current user: $ROOT" >&2;
elif ! chmod 700 "$ROOT"; then echo "could not restrict $ROOT" >&2;
elif [ -L "$BASE" ]; then echo "unsafe base symlink: $BASE" >&2;
elif ! (umask 077; mkdir -p "$BASE"); then echo "could not create $BASE" >&2;
elif [ ! -O "$BASE" ]; then echo "base is not owned by the current user: $BASE" >&2;
elif ! chmod 700 "$BASE"; then echo "could not restrict $BASE" >&2;
else break; fi;
if [ "$ROOT" = "$TEMP_ROOT" ]; then echo "no usable run root" >&2; exit 1; fi;
echo "falling back to $TEMP_ROOT" >&2; ROOT="$TEMP_ROOT";
done;
RUN_DIR="$BASE/$RUN_SLUG"; n=1;
while ! (umask 077; mkdir "$RUN_DIR") 2>/dev/null; do
if [ ! -e "$RUN_DIR" ]; then echo "could not create $RUN_DIR" >&2; exit 1; fi;
n=$((n+1)); RUN_DIR="$BASE/$RUN_SLUG-$n";
if [ "$n" -gt 99 ]; then echo "could not claim a run directory under $BASE" >&2; exit 1; fi;
done;
chmod 700 "$RUN_DIR" || exit 1;
echo "$RUN_DIR"
```

这个区块需要注意三件事。符号链接和所有权检查针对 **root**（位于共享或全局可写位置的目录）及其下的 `ce-prototype` 目录运行，因为该目录在运行之间仍然存在：`mkdir -p` 遵循已存在的符号链接，然后 `chmod` 将更改链接的目标，而不是已验证根中的任何内容。每次检查都在重试循环内，因此任一级别的不安全存储库路径都会回退到操作系统临时而不是中止 - 敌对或错误配置的 `.context` 会损害运行的持久性，而不是运行本身，并且只有也失败的临时根才是致命的。

创建目录就是它的声明方式——永远不要测试名称是否空闲然后写入，这两个一起启动的运行都会通过。没有重新加入：该块每次调用运行一次，因此第二个问题永远不会重新派生运行目录，并且既不能拆分为带后缀的同级目录，也不能采用完成的运行目录。

然后，针对每个问题，在上面打印的运行目录下创建该问题的目录：

```bash
RUN_DIR="<absolute run directory the resolution block printed>";
QUESTION_SLUG="<NN>-<question-slug>";
if [ -L "$RUN_DIR" ] || [ ! -O "$RUN_DIR" ]; then echo "unsafe run directory: $RUN_DIR" >&2; exit 1; fi;
PROTO_DIR="$RUN_DIR/$QUESTION_SLUG"; (umask 077; mkdir -p "$PROTO_DIR") || exit 1; chmod 700 "$PROTO_DIR" || exit 1;
echo "$PROTO_DIR"
```

开始（分离），将 `PROTO_DIR` 设置为分辨率打印的绝对路径：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PROTO_DIR="<absolute question directory the resolution block printed>";
if [ -L "$PROTO_DIR" ] || [ ! -O "$PROTO_DIR" ]; then echo "unsafe run directory: $PROTO_DIR" >&2; exit 1; fi;
node "$SKILL_DIR/scripts/light-webserver.js" start --root "$PROTO_DIR" --annotate
```

服务器信任`--root`——它解析路径并创建它，并且不检查任何内容——因此每次调用都会重新检查它要移交的目录。该路径通过跨单独的 shell 调用的转录到达这里，否则输入错误或过时的路径将被写入未经验证的路径。

将 `--foreground` 附加到 `start` 命令以实现前台模式。 Status 和 stop 采用相同的锚点和相同的 `PROTO_DIR` — 并且由于 Bash 调用之间两者都不会持续存在，因此每个调用都必须在自己的调用中重新设置这两个值，而不是重用 `start` 块的值：

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PROTO_DIR="<absolute question directory the resolution block printed>";
if [ -L "$PROTO_DIR" ] || [ ! -O "$PROTO_DIR" ]; then echo "unsafe run directory: $PROTO_DIR" >&2; exit 1; fi;
node "$SKILL_DIR/scripts/light-webserver.js" status --root "$PROTO_DIR"
# stop: the same command with `stop` in place of `status` (re-set both again)
```

如果`SKILL_DIR`无法解析为具体的技能目录，请勿从项目CWD中猜测。停止并报预览无法启动；不要在聊天中解决问题。

帮助器创建`screens/`和`state/`，在`screens/`中的`/`处提供最新的`.html`文件，写入`state/display-info.json`，并公开`/version`，以便默认（注释关闭）浏览器可以轮询屏幕更改。隔离网络开始通过`--annotate`：打印的 URL 是源（其中没有令牌），在服务时将覆盖层添加到浏览器在`screens/`下导航到的每个 HTML 文档（获取 HTML 部分的脚本获取原始数据），并且磁盘屏幕保持代理干净。访问该源会设置一个会话 cookie，以便覆盖可以到达等待、注释和事件；这些路由保持令牌门控。不要将令牌打印到资源管理器。原型可以使用 `?token=` 或它自己的其他查询状态。所有其他路径都是从同一路径上的 `screens/` 读取的 - `/img/blot.webp` 服务于 `screens/img/blot.webp` - 因此屏幕会保留从中复制的任何资源布局，包括嵌套。将屏幕引用的资产放在 `screens/` 下所需的路径处，或将它们内联为数据 URI。任何在 `screens/` 之外解决的问题都会被拒绝。

在移交 URL 之前，请查看渲染的屏幕 - 平台有屏幕截图，否则测量 DOM 中的布局结果。每个资产上的 200 并不是这样的检查：以错误尺寸正确加载的图像会通过它，使页面保持惰性的脚本也会通过它。检查静态的每个变体，而不仅仅是页面——共享脚手架中的一个错误看起来像是几个糟糕的设计。仅当其行为在静止时不可见时才驱动交互，在这种情况下，告诉他们尝试一些你没有尝试过的东西是你编造的主张。默认情况下，测量是存在的——计算样式在转换过程中读取，滚动事件合并——所以在事情解决之后再阅读，并在断定页面损坏之前怀疑工具。当他们能够判断这个想法时，而不是当代码正确时，你就完成了。如果您无法看到渲染结果，请在提交 URL 时说明，而不是暗示它已被检查。

仅当最新屏幕更改时才会重新加载默认启动；它不能不断地重新加载计时器。 启用「标注」后 通过流将每个更改推送到 `screens/`（屏幕或其链接的资产）下，然后页面重新加载。代理尚未应用但在重新加载后仍然有效的注释的引脚；一旦应用其注释，图钉就会离开页面，并且当会话结束时，每个图钉都会被清除。 `/version` 轮询和打开的选项卡不计为活动，因此废弃的选项卡无法使服务器保持活动状态；注释 POST 和正在运行的 `wait` 会执行此操作，因此带有等待其的代理的会话不会空闲。分离的服务器会在可以解决问题时监视所属的宿主进程，并且所有服务器会在空闲超时后退出。允许交互式 HTML。

在以下位置写入屏幕：

```text
<repo>/.context/compound-engineering/ce-prototype/<YYYY-MM-DD>-<run-slug>/
  decisions.md # 运行胶囊以获得下一个技能；不是计划
  01-<question-slug>/
    screens/
      001-<variant>.html
      img/blot.webp # 屏幕在其使用的路径引用的任何资源
      world/cast/pip.webp
    state/
      display-info.json
  02-<question-slug>/ # 仅当运行涵盖第二个相关问题时
    screens/
    state/
```

后备根在 `/tmp/compound-engineering-<uid>/ce-prototype/` 下采用相同的形状。胶囊位于运行目录并命名每个问题目录； `--root` 始终是问题目录，而不是运行目录。

## 不可触摸

选择将加载原型的浏览器 - 一个表面。将其实际请求的来源交给它。助手打印`http://localhost:<port>`。当该浏览器位于本机上时使用它。如果不是，则从 `--host 0.0.0.0` 开始，将助手返回的 URL 交给浏览器，仅将主机重写为他们可以到达的主机。仅重写主机。不要也手本地主机。访问该源会设置会话 cookie。等待将绑定地址与文件令牌进行对话。不要打印令牌。将每个接口服务的运行目录绑定到任何可以到达该端口的东西；注释和等待路由保持令牌门控——仅在用户信任的网络上执行，并在您移交 URL 时说明。

按照该主机实际的方式保持服务器处于活动状态。默认为分离 `start`。如果该主机在工具调用后捕获分离的进程或 URL 终止，请通过其长时间运行的终端附加 `--foreground`。

如果辅助路径不可用或者平台无法干净地显示本地 URL，请停止并报告。不要在聊天中解决问题——一个需要真正的产物才能决定的问题不能通过谈论来回答。
