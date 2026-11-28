# 打包脚手架

当调用指定要添加、创建或支架的包时从 SKILL.md 加载。使用SKILL.md中命名的阻塞问题工具进行提问。

**结果：** 解析器在下一次计划或审核运行时发布的Compound Pack：一个包含 `README.md` 的目录，说明该包管辖的内容，顶层的第一个规则，以及 `.compound-engineering/config.yaml` 中指向它的 `packs:` 条目。下一个消费者是捆绑的健康检查，它将包列为`pack <id>`。

**完成：**健康检查报告`pack <id>`，没有`Pack config error`或`publishes no packs`行，并且作者已经听说过布局规则以及指南中的说明。

**安全失败方向：**什么也不写，而不是写入用户未见过的目录或配置文件。存在且不为空的目标目录、配置已声明的源，或者无法要求用户每次停止脚手架并报告其将写入的内容的运行。

## 脚手架需要的事实

- 包 ID 为 kebab-case ASCII（`a-z`、`0-9`、`-`）：解析器根据其目录命名包，并且 id 在引文中显示为 `(pack: <id>, <file>)`。从 `pack:<id>` 令牌中获取，否则从请求的文字中获取；当两者都没有产生时询问。
- 默认目标是相对于存储库根 (`git rev-parse --show-toplevel`) 的`compound-packs/<id>/`。当用户命名另一个存储库相对目录时，配置条目将指向那里。
- 仅当规则是具有 `title` 和 `applies_when` frontmatter 的顶级 `.md` 时，才会发现规则；包的 `README.md` 是它的描述，而不是规则；子目录和非`.md`文件是存储。支架存在，因此第一个包以这种形状开始。
- `config.yaml` 中的实时包条目是顶级、未注释的 `packs:` 键下的 `- source: compound-packs/<id>`。捆绑模板将该密钥作为注释提供，这不是实时密钥。

## 程序

1. **解析目标。**计算 id 和目录。当目录存在并且不为空或者 `config.yaml` 已经声明了这个源时，停止，说出原因。现有的空目录就可以了。

2. **起草这两个文件。** `README.md` 在包的顶层：没有前面的内容，一行说明包的管辖内容，取自用户所说的内容，或者在他们什么也没说时提出的要求。第一条规则来自该技能目录中的`assets/pack-rule-template.md`，在README旁边保存为`<标题kebab-case>.md`。当用户描述第一条规则时，填写 `title`、`applies_when`、`tags` 以及该描述中的正文；否则保留模板的占位符，它仍然发布包并向作者显示要替换的内容。保留模板的布局提醒段落；它告诉作者删除它。

3. **起草配置更改。** 当`.compound-engineering/config.yaml`缺失时，在相同的批准下从`references/config-template.yaml`创建它。将 `  - source: compound-packs/<id>` （或用户选择的目录）附加为实时 `packs:` 列表的最后一项，与其缩进相匹配；当没有实时密钥时，将此块附加到文件末尾：

   ```yaml
   packs:
     - source: compound-packs/<id>
   ```

   保留模板的注释 `# packs:` 示例以及其他所有行。 `config.local.yaml`不是目标；团队共享的包属于跟踪文件。

4. **询问一次，显示所有内容。** 预览目录、完整的两个文件以及确切的配置行及其位置，然后询问：

   ```text
   创建Compound Pack`<id>`？
   1. 是的，写入这些文件和配置条目
   2. No thanks
   ```

   仅在批准后写入。当调用者声明运行是非交互式的，或者没有问题可以到达用户时，打印相同的预览，假设脚手架什么也没写，然后停止。

5. **通过运行状况检查进行验证。** 完全按照 SKILL.md 步骤 2 运行捆绑的 `scripts/check-health`，使用相同的 `SKILL_DIR` 锚点，并报告其 `pack <id>` 行。关于此包的 `Pack config error` 或 `publishes no packs` 行意味着脚手架尚未完成：修复原因并再次运行检查。

6. **告诉作者。** 一句话：一条规则只有当它是顶级`.md`与`title`和`applies_when`时才被发现； pack 文件夹中的其他所有内容都是存储，`README.md` 是描述。指向 `https://everyinc.github.io/compound-engineering-plugin/guides/packs/`，“包布局”，查看带注释的树。在第 3 阶段摘要中，报告该包是否已编写或用户拒绝。
