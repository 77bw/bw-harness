# 保留输出

尊重明确的用户目的地。否则，使用项目在已解析的 CE 产物根下建立的持久产物约定；不要发明第二个规范计划。此引用控制保留文档的直接使用；聊天结果和呼叫者拥有的产物保留其现有的交付合同。

<!-- ce-docs-root:start -->
**在组成任何产物路径之前解析 CE 产物根 `<root>`。**

- **仅从 `<repo-root>/.compound-engineering/config.yaml` 读取** `docs_root` (`<repo-root>` = `git rev-parse --show-toplevel`)。不要从`config.local.yaml`开始阅读。取消设置 -> `<root>` 为 `docs`，与之前完全相同。
- **验证**设置值：一个存储库相对目录，其真实的符号链接解析路径保留在存储库内，既不是存储库根目录，也不是位于 `.git/` 下。否则，会因命名 `docs_root` 和值时出错而停止 - 永远不会回退到 `docs`。
- **使用** `<root>` 作为唯一的产物位置：如果不存在则创建它，将每个路径与该技能自己的子目录组成 `<root>/<subdir>`，并且永远不要读取 `docs`。
<!-- ce-docs-root:end -->
