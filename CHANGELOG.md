# 变更记录

## 1.0.0

- 内置 Matt 与 CE 固定修订、Pi 子 Agent 运行依赖、三项自研入口、Copier 模板与中文指南。
- `pi-subagents` 保持 Pi 1.1 兼容版本；锁定覆盖其 `undici` 依赖，避免 npm audit 已报告的旧版安全问题。安装要求 Node ≥22.19。
- 兼容状态见 guides/installation.md。探索分支包含 ce-prototype、ce-explain、ce-pov、ce-bakeoff 和 ce-ideate；验证器报告缺失目标及调用方。
