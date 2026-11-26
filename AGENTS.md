# 维护 BW Harness

这是跨项目的 Skill Pack，不是业务项目脚手架。三个 BW 入口的执行契约在各自的 SKILL.md；项目文档 seed 由 setup 随包分发。Guides 面向用户。更改执行入口或可达分支时同步指南与真实案例。

先读 upstream.lock.yml。改上游时从固定修订派生、保留版权和可重放差异，分别验证原始与分发资源。不要通过扩大排除列表修复断链。依赖、脚本和宿主调用按实际到达的路径测试；Git 交付沿用 CE 原生分支、审查与发布约定。

包内检查：npm ci --legacy-peer-deps --ignore-scripts；python3 scripts/validate-package.py；uvx --from pytest pytest -q tests。发布前还需隔离安装、实际模型调用、跨会话接续、词表往返和合成仓 Git 交付证据。静态检查不代表宿主通过；凭据、会话、原始报告和个人配置不进版本库。
