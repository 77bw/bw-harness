# ce-explain：解释已有行为

条件入口，通常由 ce-brainstorm、ce-plan 或 ce-debug 在需要时调用，不是默认必经步骤。先提供项目约束和脱敏输入；已有明确结论时跳过。

Pi 示例：`/skill:ce-explain 追踪一个 UTF-8 长度字段从入口到校验失败的路径，区分源码证据和推测。`

结果用于澄清选择，不代替正式计划或测试。写入原型、启动服务、调用外部资源或修改项目文件前核对授权。不要自动提交。找不到入口先检查包版本及重名来源。

[原生说明与资源](../../skills/ce-explain/SKILL.md) · [宿主支持情况](../installation.md) · [CE 固定版本与许可](../../upstream.lock.yml)
