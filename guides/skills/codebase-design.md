# codebase-design：模块边界

在需要「模块边界」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:codebase-design 比较调用者必须自己拼装长度字段与 encode(payload) 两种接口。`

**预期结果与边界**：列出复杂度归属、接口及测试边界；不是实施计划。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：Matt Pocock，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/codebase-design/SKILL.md)。
