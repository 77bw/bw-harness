# 神器根

仅当存档到存储库时，解释器才会位于`<root>/explainers/`下，并且可以在`<root>/solutions/`下阅读学习内容。仅当您组成这样的路径时才解析`<root>`；仅从头开始或外部概念运行永远不会构成一个。将解析的路径传递给任何子代理，而不是配置。

<!-- ce-docs-root:start -->
**在组成任何产物路径之前解析 CE 产物根 `<root>`。**

- **仅从 `<repo-root>/.compound-engineering/config.yaml` 读取** `docs_root` (`<repo-root>` = `git rev-parse --show-toplevel`)。不要从`config.local.yaml`开始阅读。取消设置 -> `<root>` 为 `docs`，与之前完全相同。
- **验证**设置值：一个存储库相对目录，其真实的符号链接解析路径保留在存储库内，既不是存储库根目录，也不是位于 `.git/` 下。否则，会因命名 `docs_root` 和值时出错而停止 - 永远不会回退到 `docs`。
- **使用** `<root>` 作为唯一的产物位置：如果不存在则创建它，将每个路径与该技能自己的子目录组成 `<root>/<subdir>`，并且永远不要读取 `docs`。
<!-- ce-docs-root:end -->
