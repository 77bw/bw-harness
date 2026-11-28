# 创建切换

在编写交接之前需要阅读。

## 建立交接

1. 提炼当前目标和用户的最新意图。如果提供了焦点，请将其设为 `resume_focus`。
2. 仅检查解释当前存在的内容所需的工作空间状态。使用上下文中已经存在的项目的活动说明和约定。
3. 指出计划、问题、提交、差异、文档和相关文件，而不是复制其内容。
4. 编辑机密、凭据和不相关的个人信息。仅当下一个代理需要时才保留操作路径。
5. 使用现有功能编写或发布文档。如果用户请求其他路径、文件夹、格式或发布目的地，请遵守它并使用适当的可用功能，包括相关时已安装的发布技能。除非用户要求，否则不要创建持久托管存储副本；发布能力可以使用其普通的临时工作文件。

## 默认托管存储

当用户没有选择其他目标时，使用以下 shell 块解析托管根：

```bash
SCRATCH_ROOT="/tmp/compound-engineering-$(id -u)";
[ ! -L "$SCRATCH_ROOT" ] && (umask 077; mkdir -p "$SCRATCH_ROOT") 2>/dev/null && [ ! -L "$SCRATCH_ROOT" ] && [ -O "$SCRATCH_ROOT" ] && [ -w "$SCRATCH_ROOT" ] || SCRATCH_ROOT="${TMPDIR:-/tmp}/compound-engineering-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
HANDOFF_DIR="$SCRATCH_ROOT/ce-handoff/<repo-namespace>";
(umask 077; mkdir -p "$HANDOFF_DIR") || exit 1; chmod 700 "$HANDOFF_DIR" || exit 1;
```

在 `$HANDOFF_DIR/<topic>.md` 处写入 Markdown 快照。

使用可读的主题别名作为文件名。当Git上下文存在时，使用经过清理的存储库名称加上稳定的根提交前缀作为存储库命名空间；否则使用`general`。来自同一存储库的工作树共享名称空间，并通过 frontmatter 保持可区分性。默认情况下不要在路径中放置时间戳或唯一 ID； `created_at` 承载着发现的年表。以原子方式、独占方式保留最终候选文件名；发生冲突时，使用最小的可用数字后缀重试，而不是覆盖切换。切勿检查可用性然后再写。在平台支持权限的情况下，将目录和文件保持为用户私有。

## 前置合同

对于托管商店中的 Markdown 交接，请使用扁平 YAML frontmatter：

```yaml
---
artifact_contract: "ce-handoff/v1"
created_at: "Current ISO-8601 UTC timestamp"
title: "简短的描述性标题"
summary: "在搜索结果中区分这种切换的一句话"
keywords: ["keyword-one", "keyword-two"]
cwd: "/absolute/capture/path"
resume_focus: "Optional next-session focus"
repository: "Sanitized repository identifier without embedded credentials"
repo_root_sha: "First root commit when available"
branch: "Captured branch when available"
head: "Captured HEAD when available"
worktree_path: "Captured worktree when relevant"
---
```

必需的托管商店字段为 `artifact_contract`、`created_at`、`title`、`summary`、`keywords` 和 `cwd`。使用JSON兼容YAML双引号和转义序列化每个生成的字符串标量和字符串数组元素；切勿将原始会话文本插入为不带引号的 YAML 标量。当提供或清除时，请包括 `resume_focus`。仅在适用时包括 `repository`、`repo_root_sha`、`branch`、`head` 和 `worktree_path`。不要添加可变的生命周期字段。在用户控制的目的地或以其他格式，在格式支持时保留等效的发现和定向元数据；不要让这个YAML形状阻挡所请求的目的地。

## 身体契约

选择最能将这一特定会话传达给下一位客服人员的部分和文档组织。下面的标题是有用的覆盖范围的示例，而不是必需的或封闭的模板：添加新部分或组合、重命名、重新排序，并在使切换更清晰时省略示例。

仅包含新特工无法安全推断的内容，来自：

- 客观和当前的用户意图
- 工作已完成
- 决策、限制和被拒绝的替代方案
- 当前状态——当各项工作的成熟度不同时，比如哪些工作已完成、哪些工作正在进行中（以及其中剩余的内容）或哪些工作尚未开始
- 权威引用文档
- 未完成的工作、阻碍、依赖性和脆弱的本地状态
- 失败的方法已经被放弃，错误的路径下一个代理可能会重试
- 已执行验证并观察到故障
- 合理的后续步骤（独家分叉作为替代方案；相关的连续工作作为一条路径 - 与简历使用的框架相同）
- 可能有帮助的相关安装技能（如果有）

切换是您对会话的说明，因此无论下一个代理将意图声明或决定视为用户的，请说明是用户的、您的推论还是您自己的决定。

将主体默认为接收代理可以验证的地面实况：什么存在、什么是部分的、什么缺失以及什么依赖于什么。更喜欢这种状态框架而不是针对下一个代理的工作订单。在不授予操作权限的情况下加载上下文的定向辅助工具仍然有用，例如，在决定之前要阅读哪些文档或文件。仅当用户要求切换包含显式指令时才携带显式指令；将用户请求的指示与状态和证据区分开来。 Resume 仍将文档视为不受信任的上下文，并在执行操作之前等待当前用户。

保持切换指针在前。对于每个所需的参考，请命名其中特别重要的内容（而不仅仅是路径），并在缩小着陆区域时添加线路范围。首选存储库文件的存储库相对路径，由存储库、分支和 HEAD 元数据锚定一次。仅对机器本地捕获上下文或未提交、未跟踪、忽略或临时状态使用绝对路径，并将它们标记为机器本地。

## 报告

仅在确认目的地包含切换后才将创建视为完成。对生成的切换捕获的内容进行简洁、特定于上下文的摘要，以便用户无需打开它即可验证其实质内容；不要强加固定的摘要模板。然后报告最终路径或 URL、适用的保留或访问限制以及任何警告。托管 `/tmp` 存储由操作系统管理，并且不是永久性的。它的自动发现假设接收会话可以看到相同的主机文件系统；否则告诉用户将切换传输或发布到接收者可见的位置并从该显式源恢复。

使用最终路径或 URL 以及正文中的渲染规则，通过一个受保护的可复制命令结束创建响应：

```text
<rendered resume invocation>
```

需要时引用源代码，以便可以逐字粘贴命令。不要生成较长的恢复提示。
