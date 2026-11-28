# 维护 BW Harness

这是 Skill Pack，不是生成后的 Python 项目。业务模板仅来自 templates/python。先查 upstream.lock.yml；不要就地改 vendor 资源却不记录补丁。修改入口时同步对应 guides/skills 指南。

包内检查：npm ci --legacy-peer-deps --ignore-scripts；python3 scripts/validate-package.py；uvx --from pytest pytest -q tests。发布门禁还需隔离宿主真实安装、调用和跨会话试点；静态检查不能代替。任何业务项目的 Git 交付另需授权。测试使用合成数据，报告、会话、凭据不得纳入版本库。
