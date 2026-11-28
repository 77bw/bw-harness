# 工作约定
开始读 GLOSSARY.md、docs/status.md 和当前计划，核对 Git 与测试。已确认需求不再访谈。
复杂变更：grill-with-docs → ce-plan → ce-work mode:return-to-caller → project-governance。若无法限制交付尾部则停止原生实施，改为本地实施和独立审查。
只维护 docs/plans 中一个实施计划。正式代码进 src；实验不得被正式代码导入。测试向量脱敏，原始证据仅存 .local。
结论注明 VERIFIED / HYPOTHESIS / REFUTED / STALE 与证据；术语只进 GLOSSARY，经验有复用价值才 ce-compound。最后原地更新 status。
运行 uv run pytest、uv run ruff check .、uv run ruff format --check . 和 python scripts/check_structure.py。不自动提交、推送、建 PR、修改全局规则或删除唯一证据。

BW 只提供已注册的本地工程路线。上游提到的远程 PR、发布、营销、产品战略和自动交付不属于本包；不要推荐、安装或代跑未注册的 Skill。导航用 bw-help，遇到未启用的路线，说明边界并返回调用方。
