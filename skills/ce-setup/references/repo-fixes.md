# 存储库本地修复（第 2 阶段）

## 内联运行状况检查等效项（第 2 步后备）

当捆绑的 `scripts/check-health` 不可用时，手动执行这些检查并报告相同的结果：

1. 使用 `command -v` 检查可选工具：`agent-browser`、`gh`、`jq`、`ast-grep`、`ffmpeg`。
2. 如果在 git 存储库中，请使用 `git rev-parse --show-toplevel` 解析存储库根。
3. 检查存储库根目录中是否有过时的 `compound-engineering.local.md`。
4. 检查`.compound-engineering/config.yaml`是否存在。
5. 检查`.compound-engineering/config.local.yaml`是否存在，如果存在则`git check-ignore -q .compound-engineering/config.local.yaml`是否成功。
6. 当模板可读时，比较`.compound-engineering/config.example.yaml`与`references/config-template.yaml`；否则报告示例刷新必须手动完成。
7. 当 `${CODEX_HOME:-$HOME/.codex}/AGENTS.md` 包含独立的 `<!-- BEGIN COMPOUND CODEX TOOL MAP -->` 行，后跟独立的 `<!-- END COMPOUND CODEX TOOL MAP -->` 行时，报告旧式复合 Codex 工具图。
8. 当 `node -p 'process.versions.node'` 为 22.13 或更新且 `command -v npx` 成功时，报告`node`行可用于跨模型对等；否则请指出两者中哪一个缺失或太旧。

该文件在两个点读取：每当捆绑的运行状况脚本不可用时，从步骤 2 开始读取，对于上面的内联等效项；在任何第 2 阶段写入之前，一旦第 3 步确定存在可写签出以及哪些报告的问题需要修复。用屏蔽提问工具`references/communication.md`名字提问。维护生成的示例文件是此阶段自行完成的工作 - 步骤 5 的刷新以及删除被取代的 `config.local.example.yaml`。仅当用户批准时，才会提供并应用对用户拥有的文件的每次更改。

## 第 2 阶段：修复回购本地问题

解析存储库根目录 (`git rev-parse --show-toplevel`)。下面的所有路径都是相对于存储库根目录的，而不是当前工作目录。

### 步骤 4：删除过时的本地配置

如果 `compound-engineering.local.md` 存在于存储库根目录，请说明它已过时，因为审查代理选择是自动的，并且幸存的计算机本地设置现在位于 `.compound-engineering/config.local.yaml` （可选覆盖）中。团队默认值位于`config.yaml`。

请问现在是否删除。仅在用户批准后才删除。

### 第 5 步：刷新示例配置

将 `references/config-template.yaml` 复制到 `<repo-root>/.compound-engineering/config.example.yaml`，根据需要创建目录。该文件已提交到存储库，并且应始终反映最新的可用设置。当运行状况报告显示该示例是由较新的插件编写的时，请不要理会它，这样较旧的插件就不会回滚它。

如果新示例存在后剩余的 `<repo-root>/.compound-engineering/config.local.example.yaml` 仍然存在，请将其视为过时的生成示例（而不是用户配置）并使用 `trash` 删除它（永远不要 `rm`）。

如果当前平台无法定位捆绑的模板，则打印失败的源模板路径，并告诉用户示例配置无法自动刷新。

### 步骤 5a：刷新 Repo 配置文件

当运行状况报告显示 `config.yaml` 是从旧模板写入时，在任一文件中命名已停用的配置键，或调用 `config.local.yaml` 旧本地模板的完整副本，请阅读 `references/config-refresh.md` 并遵循它。报告称文件是由较新的插件编写的或无法刷新的文件保持不变。

### 第 6 步：创建 Repo 配置（如果丢失）

如果 `.compound-engineering/config.yaml` 不存在，请主动创建它，即使健康状况为绿色。用户应该知道，这是一个共享文件，团队可以在其中打开 Compound Engineering 设置，每个设置都会被注释掉，因此在有人启用某个设置之前不会发生任何变化，并且拒绝保留默认设置。

如果用户同意，则将`references/config-template.yaml`复制到`<repo-root>/.compound-engineering/config.yaml`。仅通过步骤 5a 验证的刷新或下面的修复来更改现有的 `config.yaml` 或 `config.local.yaml`。

如果`config.local.yaml`已经存在，则保留它。创建后（或者如果两个文件都已存在），命名将隐藏新团队文件的普通本地键。如果本地仍然有`docs_root`，则表示它被忽略并提出将其移至`config.yaml`。

不要创建`config.local.yaml`。

### 步骤 6a：修复无效的 CE 工作首选项

当健康报告标记CE Work实施引擎不可用或无效，或报告格式错误的休眠`work_engine_preferences`时，不要猜测预期的接收者。已停用的路由键（例如 `work_engine_target`）是要删除的步骤 5a，而不是此步骤。解释确切报告的问题，从用户指定的 harness/model 顺序中派生出有效的有序 `work_engine_preferences` 块（或者删除格式错误的休眠首选项，并在需要默认本机时使用 `work_engine_mode: off`），并显示完整的替换块。编辑提供失败值的图层。如果坏的普通密钥仅在`config.yaml`中，请在预览后编辑该文件。不要在新的本地替代背后隐藏破碎的团队价值。保留所有不相关的设置。重新运行运行状况检查并要求其在设置完成之前报告本机或预期的规范化有序列表。

当健康报告警告`work_engine_effort`时，引擎的健康状态不会改变，警告会说明`ce-work`对该值的作用。不是地图的值或未知宿主的条目不会请求任何内容。 `cursor` 条目不同：没有游标路由可以同时运行，因此`ce-work` 将首选项列表中的游标条目视为不可用，直到该条目被删除。关键是从利用工具到该利用工具自身的努力水平之一的映射。询问用户希望为每个宿主付出什么努力而不是猜测，显示替换地图，并编辑警告名称的图层。重新运行运行状况检查并要求警告消失。

### 步骤6b：修复无效`docs_root`

当运行状况报告将 `docs_root` 标记为无效时，请解释其给出的确切原因（绝对、逃避存储库、`..` 遍历、存储库根、`.git/` 或非目录组件）以及结果：在修复之前不会写入 CE 产物，因为 `docs_root` 失败关闭，而不是默默地回退到 `docs`。 `docs_root` 只能从 `.compound-engineering/config.yaml` 读取。 `config.local.yaml` 中的 `docs_root` 将被忽略 — 如果本地仍有一个，请说明并提出将其移至 `config.yaml`。提议将跟踪值更正为用户命名的有效存储库相对目录，或从 `config.yaml` 中删除错误的 `docs_root` 密钥。删除它达到默认`docs`。在用户批准后仅编辑这些密钥；保留所有不相关的设置。重新运行运行状况检查并要求其在安装完成之前报告已解决的产物根。

### 第 7 步：确保忽略本地配置

如果`.compound-engineering/config.local.yaml`存在并且不被`.gitignore`覆盖，建议添加：

```text
.compound-engineering/*.local.yaml
```

仅当用户批准时才将条目附加到 repo-root `.gitignore`。不要覆盖不相关的`.gitignore`内容。

### 第 8 步：提供 Gitignore CE 暂存空间

保留本地草稿的技能写在`.context/compound-engineering/`下。使用 `git -C <repo root> check-ignore -q .context/compound-engineering/` 探测覆盖范围 — 带有尾部斜杠，因此现有的仅限目录的规则在目录存在之前进行计数，并锚定到存储库根目录，因为这是附加条目的位置 — 当未覆盖时，建议添加：

```text
.context/compound-engineering/
```

仅当用户批准时才将条目附加到 repo-root `.gitignore`。不要覆盖不相关的`.gitignore`内容。

与步骤 7 不同，这不会等待路径存在。在那里写入的技能在第一次写入时会提供相同的条目，因此从不使用这些技能之一的存储库永远不需要该行 - 在此处添加它仅意味着提示永远不必触发。

### 第 9 步：在知识库中指定代理，并提供常规指令

每当存储库具有根代理指令文件（`AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 或此项目使用的等效文件）时运行。当一个文件仅`@`-包含另一个文件时，实质性文件就是目标。没有这样的文件：跳过这一步并在摘要中注明；安装程序永远不会创建一个。

**结果：** 读取该文件的代理了解到知识存储存在于已解析的`<root>/solutions/`以及相关的时间，并且该文件包含用于捕获学习内容的常规指令以及用于代理自己的聊天回复（如果用户需要）的指令。每个添加项均单独提供，并以其确切位置进行预览，并且仅在批准后应用。

**存储提及。** 读取文件并从语义上判断，而不是通过字符串匹配，读者是否会学到三件事：在具体路径中存在文档化解决方案的存储，其形状足以搜索它（类别，YAMLfrontmatter字段，例如`module`，`tags`，`problem_type`），以及在文档区域中实现或调试时相关。当精神满足时，什么也不提供。否则，以文件自己的风格起草最小的添加内容：最接近的现有部分（目录列表、体系结构树、约定块）中的一行击败新标题，而新标题是最后的手段。保持语气是信息性的，而不是命令式的，因为当工作流已经搜索时，命令式会导致冗余读取。写入具体的解析路径，切勿使用 `<root>` 占位符，因为人们和无插件代理会读取此文件。目录列表的校准：

```text
<root>/solutions/ # 针对过去问题（错误、最佳实践、工作流程模式）的记录解决方案，按类别通过YAML frontmatter（模块、标签、problem_type）进行组织
```

**知识沉淀指令。** 仅当存储库将存储视为可跟踪的、已提交的数据时才提供它：git 跟踪已解析的 `<root>/solutions/` 下的至少一个文件（`git ls-files` 非空；未跟踪或 gitignored 目录不是证据），或者用户刚刚接受了存储提及。当文件已经包含调用 `ce-compound` 的常设指令（以任何措辞）时，请跳过该提议，该指令在完成检查点运行并让技能决定课程是否合格。当现有指令让代理首先决定课程是否值得文档时，建议将其替换为同类的捆绑变体（首先询问或自动）。这种预先判断会跳过该技能在测试或编码标准中所包含的课程。否则提供。用户应该了解到，代理会记录课程作为测试、编码标准或下班后的学习，纠正对某些行为的错误信念，这样下一个代理就不会重复错误。选择是代理人首先询问，他们在没有询问或没有指示的情况下进行操作。

从 Skill 目录读取 `assets/compounding-directive.md`，将选中的正文原样插入项目指令文件；该措辞是通过测试确定的，因此请勿对其进行解释。当它落在约定或工作协议块中时，将其放置在知识库入口旁边，否则放置在文件说明代理应如何工作的块中。匹配周围的形式（项目符号列表中的项目符号、散文中的段落）。说明文本的去向以及要求代理执行的操作，并在用户询问时显示确切的文本。仅在批准后追加，文件的其余部分保持不变。

**聊天注册指令。** 每当此步骤运行时提供它。仅当文件已包含涵盖捆绑文件的所有三个部分的指令时才跳过要约：报告边界（即将编写的面向用户的报告、摘要或移交）、调用（使用 `ce-noslop` 技能进行编写）和排除项（代码、配置、逐字引用、用户要求按书面形式发布的文本）。部分指令，例如仅命名边界的指令或通用的“简单书写”，或不相关的书写规则仍然可以得到报价。用户应该了解到，代理的报告和摘要将被简单地书写，没有人工智能书写习惯，并且他们要求发布的代码和文本不会被修改。

从 Skill 目录读取 `assets/noslop-directive.md`，将其正文原样插入项目指令文件；不要改写。当知识沉淀指令落地或已经存在时，将其放在知识沉淀指令旁边，否则将放在知识沉淀指令所在的位置。与周围的形状相匹配。说明文本的去向以及要求代理执行的操作，并在用户询问时显示确切的文本。仅在批准后追加，文件的其余部分保持不变。

在第 3 阶段总结中报告所有三个结果。

### 第 10 步：提供项目审查文档的起始草稿

从该技能的目录中读取`references/project-docs.md`并遵循它。它提出起草或更新`CODING_STANDARDS.md`、`REVIEW.md`以及指向它们的代理指令行和 AI 审查者文件的提议，这些文件是根据存储库自己的审阅历史记录构建的，并且在用户批准草稿之前不写入任何内容。
