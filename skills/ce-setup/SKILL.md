---
name: ce-setup
description: "检查 Compound Engineering 的工具和存储库配置并修复它发现的内容，使用 `pack:<id>` 搭建Compound Pack，或者起草和刷新编码标准并审查拉取请求历史记录中的文档。在设置或诊断 Compound Engineering 时使用，或者在创建或更新 CODING_STANDARDS.md 或 REVIEW.md 时（包括按计划）使用。"
argument-hint: "[包装：<id> |标准] [mode:non-interactive]"
---

> 本包以简体中文撰写说明、选项及面向用户的输出。Skill 名称、命令、路径、字段、枚举、原文引述及要求精确匹配的契约标记保持原样。

# Compound Engineering 设置

## 非交互式运行

当参数包含`mode:non-interactive`时，或者当请求使无人值守意图明确无误时（例如计划或CI作业，或者调用者要求“无头”、“无人值守”或“无问题”运行），以非交互方式运行。 “自动”本身并不是那个信号：它表示安装程序何时运行，而不是是否有人可以回答。当信号缺失或不清楚时，交互式运行。在读取其余参数之前删除标记。非交互式运行不询问任何内容，并遵循 `references/non-interactive.md`，它替换此文件及其参考中的每个提议、问题和批准。

## 互动方式

在交互式运行中，使用主持人的阻塞问题工具提出以下每个问题，并且切勿默默地跳过或自动配置。在您第一次提供之前，请从该技能的目录中阅读`references/communication.md`。它说明了如何使用该工具以及每个优惠、问题和预览必须告诉用户什么。

## 包装脚手架

当调用指定要添加、创建或搭建的Compound Pack（`pack:<id>`参数，或相同的文字请求）时，从该技能的目录中读取`references/pack-scaffold.md`并按照它代替阶段 1-2：仅在用户批准后写入包及其配置条目，运行运行状况检查本身，并报告到阶段 3（摘要）。

## 审查文档

当调用要求起草、刷新或更新编码标准或审查文档（`standards`参数或相同的文字请求）时，请阅读`references/project-docs.md`并遵循它来代替阶段 1-2，即使请求指定了一个文件，也要起草整套文件。报告进入第 3 阶段。

## 伪影根分辨率

每个读取或写入 CE 拥有的产物树（`solutions`、`plans` 等）的Compound Engineering 技能都通过此规则解析其根。步骤 2 报告已解析的根。

<!-- ce-docs-root:start -->
**在组成任何产物路径之前解析 CE 产物根 `<root>`。**

- **仅从 `<repo-root>/.compound-engineering/config.yaml` 读取** `docs_root` (`<repo-root>` = `git rev-parse --show-toplevel`)。不要从`config.local.yaml`开始阅读。取消设置 -> `<root>` 为 `docs`，与之前完全相同。
- **验证**设置值：一个存储库相对目录，其真实的符号链接解析路径保留在存储库内，既不是存储库根目录，也不是位于 `.git/` 下。否则，会因命名 `docs_root` 和值时出错而停止 - 永远不会回退到 `docs`。
- **使用** `<root>` 作为唯一的产物位置：如果不存在则创建它，将每个路径与该技能自己的子目录组成 `<root>/<subdir>`，并且永远不要读取 `docs`。
<!-- ce-docs-root:end -->

## 第一阶段：诊断

### 第 1 步：确定插件版本

当平台公开时，通过读取插件元数据或清单来检测已安装的复合工程插件版本。如果无法确定版本，请跳过此步骤。

如果找到版本，则通过 `--version` 将其传递给检查脚本。否则省略该标志。

### 第 2 步：运行健康检查

运行脚本之前，显示：

```text
Compound Engineering -- 检查您的环境...
```

运行捆绑的检查脚本。将 `SKILL_DIR` 设置为您加载此 `ce-setup` SKILL.md 的绝对目录 — Bash 工具的 CWD 是用户的项目，而不是技能目录，因此裸露的 `scripts/` 路径将无法解析：

```bash
SKILL_DIR="<absolute path of the directory containing this SKILL.md>";
if [ -f "$SKILL_DIR/scripts/check-health" ]; then bash "$SKILL_DIR/scripts/check-health" --version VERSION; else echo "Bundled health script not found at $SKILL_DIR/scripts/check-health; run the inline checks from ce-setup instead."; fi
```

如果步骤 1 无法确定版本，请使用不带 `--version VERSION` 的相同命令。

如果该脚本不可用，请运行 `references/repo-fixes.md` 中列出的内联等效脚本。

向用户显示诊断输出。运行状况报告包括已解析的产物根以及提供它的配置层（根据上面的产物根解析）；显示该行，以便操作员可以确认 CE 产物将写入何处。缺少 `config.yaml` 是报告的缺勤，而不是项目问题。

### 第 3 步：决定是否需要修复

Repo-local 修复了运行状况报告名称仅适用于报告诊断的结账的问题。如果第 2 阶段将写入不同的可写签出，请首先诊断该签出。插件版本和可选工具等会议级别的发现仍然来自本次会议的第一阶段。

在健康报告之后，根据可写结帐可用性决定第 2 阶段：

- 如果此会话具有可写的 git checkout，请在本地运行第 2 阶段，包括当 `project_issues` 为 0 时。第 2 阶段始终刷新示例，并在该文件丢失时始终提供创建 `config.yaml` 的功能。
- 如果此会话没有可写签出，但用户命名了存储库并且工具公开了具有可写签出的远程存储库工作界面，请在该界面上运行第 2 阶段，并在第 3 阶段报告远程存储库本地修复。
- 否则跳过阶段 2 并转到阶段 3，表示跳过了存储库本地写入，因为没有可用的可写签出。

两个报价涉及这台机器而不是结帐，因此无论第二阶段是否运行，它们都有效。如果报告命名了旧的复合工具图Codex，请提出将其从该技能目录中的`references/legacy-codex-tool-map.md`删除。如果捆绑的运行状况脚本报告 `node` 行可用，请在 `references/acpx-cache-warm.md` 之后为跨模型对等点提供预热 npm 缓存。

第 2 阶段修复每个项目问题的报告名称，每个问题都有自己的`references/repo-fixes.md` 步骤。其中包括过时的`config.yaml`、已退役的配置密钥、报告标记为不可用或无效的`ce-work`实现引擎，以及格式错误的休眠`work_engine_preferences`或`work_engine_effort`。

## 第 2 阶段：修复回购本地问题

在进行任何存储库本地更改之前，请从此技能的目录中读取`references/repo-fixes.md`。它修复报告名称的每个项目问题并执行步骤 4-10：删除过时的 `compound-engineering.local.md`、刷新示例配置、刷新保留设置的过时配置文件、提供创建 `config.yaml`、修复无效的 `work_engine_preferences` 和 `docs_root`、两个 `.gitignore` 提供以及代理说明提供（知识库提及、知识沉淀指令，以及`ce-noslop`的聊天注册指令），以及起草项目审查文档的提议。

仅当用户批准时，才会提供并应用对用户拥有的文件的每次更改。

## 第三阶段：总结

**用户可运行的调用渲染。** 使用当前主机公开的注册来渲染 `ce-setup` 和已安装的 `bw-help`：在 Pi 上使用 `/skill:<name>`，在 Codex 上使用编目 `$<name>`，在 Claude Code 上使用斜杠命令，包括任何已安装的插件命名空间。如果主机公开不同的拼写，请使用确切的目录条目，而不是猜测的别名。仅显示一种形式。

写出`references/summary.md`描述的摘要。以这两行结束，并填充渲染的调用：

```text
随时运行`<rendered invocation>`重新检查。
运行 `<rendered bw-help invocation>` 询问哪种技能适合或接下来会发生什么。
```
