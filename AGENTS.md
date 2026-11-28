# 维护 BW Harness

这是跨项目的 Skill Pack，不是业务项目脚手架。三个 BW 入口的执行契约在各自的 SKILL.md；项目文档 seed 由 setup 随包分发。Guides 面向用户。更改执行入口或可达分支时同步指南与真实案例。

先读 upstream.lock.yml。改上游时从固定修订派生、保留版权和可重放差异，分别验证原始与分发资源。不要通过扩大排除列表修复断链。依赖、脚本和宿主调用按实际到达的路径测试；Git 交付沿用 CE 原生分支、审查与发布约定。

同步默认只读：`python3 scripts/sync-upstream.py`。有本地固定源码时加 `--cache <含 matt/ 和 ce/ 的目录>`。只有在已核对具体改动与回归用例后，才在 POSIX 宿主用 `--record skills/<名称>` 重录该资源的补丁及锁；再运行默认重放。不要用重录修饰未知的校验失败。

包内检查：npm ci --legacy-peer-deps --ignore-scripts；python3 scripts/validate-package.py；uvx --from pytest pytest -q tests。发布前还需隔离安装、实际模型调用、跨会话接续、词表往返和合成仓 Git 交付证据。静态检查不代表宿主通过；凭据、会话、原始报告和个人配置不进版本库。

分发内容使用简体中文：Skill 正文、用户可见提示、子代理提示、引用说明及模板均保持中文。Skill 名、调用方式、代码、路径、字段、精确契约标题、原文引用及上游许可证保持原样；模板中的示例正文仍应使用中文。上游更新时重放并复核译文与协议对齐。
