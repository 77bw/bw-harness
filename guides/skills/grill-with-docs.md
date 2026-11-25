# grill-with-docs：需求与领域对齐

在需要「需求与领域对齐」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:grill-with-docs 本地消息的长度指字节还是字符？给出反例，再确认术语。`

**预期结果与边界**：确认定义写 GLOSSARY，重要取舍写 ADR；把已确认限制原样交给 ce-plan。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：Matt Pocock，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/grill-with-docs/SKILL.md)。
