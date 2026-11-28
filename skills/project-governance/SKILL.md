---
name: project-governance
description: 项目收尾、结构检查、术语去重或旧项目分批治理时使用。
---

check/migrate：调用 ../setup-bw-harness/scripts/setup.py 的对应模式；先只读核对 Git、测试基线、CONTEXT/CONCEPTS、临时脚本和唯一证据。列出逐文件建议、风险和回退方法。未确认不迁移。close：核对变更范围，实际运行检查器、Ruff 和 pytest，独立审查代码；定位临时产物但不删除唯一副本。只将确认术语合并到 GLOSSARY；按主题更新 research。仅非显然、已验证且可复用经验交给 ce-compound，已有则不重复。最后原地更新 docs/status.md，列出命令、结果、未解决项及下一步。未经授权不得提交、推送或改规则。
