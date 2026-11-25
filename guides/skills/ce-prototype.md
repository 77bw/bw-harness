# ce-prototype：用可丢弃原型确认交互选择

条件入口，通常由 ce-brainstorm、ce-plan 或 ce-debug 在需要时调用，不是默认必经步骤。先提供项目约束和脱敏输入；已有明确结论时跳过。

Pi 示例：`/skill:ce-prototype 在 .local 中对比两种消息展示方式，先说明是否需要监听本机端口；不要接入真实数据。`

结果用于澄清选择，不代替正式计划或测试。写入原型、启动服务、调用外部资源或修改项目文件前核对授权。不要自动提交。找不到入口先检查包版本及重名来源。

[原生说明与资源](../../skills/ce-prototype/SKILL.md) · [宿主支持情况](../installation.md) · [CE 固定版本与许可](../../upstream.lock.yml)
