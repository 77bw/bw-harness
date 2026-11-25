# 快速上手

先在包根目录运行 `uvx --from pytest pytest -q tests`，它会在临时 Git 仓库用真实 Copier 和 uv 生成轻量/API 项目，并执行导入与 API 测试。

在有模板提交的本地克隆完成[注册](installation.md)后，进入一个空业务目录，通过 `/skill:setup-bw-harness` 指定包名 demo。生成后运行 `uv run pytest -q`、`uv run ruff check .`、`uv run ruff format --check .`、`uv run python scripts/check_structure.py`。确认 `.copier-answers.yml` 指向预期来源和修订。

接着请求 `/skill:bw-help 我想开发一个本地消息编码器`。已有项目不要运行 new；先请求只读 check。
