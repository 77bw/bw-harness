# grilling：访谈依赖

在需要「访谈依赖」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:grilling 针对零长度消息是否有效，一次问一个会影响设计的问题。`

**预期结果与边界**：输出待决问题与已确认回答；通常由 grill-with-docs 调用，不重复访谈。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：Matt Pocock，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/grilling/SKILL.md)。
