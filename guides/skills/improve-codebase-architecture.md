# improve-codebase-architecture：架构改善

在需要「架构改善」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:improve-codebase-architecture 找出编解码层与 API 路由间泄漏的格式知识，先不要改代码。`

**预期结果与边界**：给出候选及报告；选定后再深入，对报告落点先确认。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：Matt Pocock，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/improve-codebase-architecture/SKILL.md)。
