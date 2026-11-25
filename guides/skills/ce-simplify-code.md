# ce-simplify-code：保持行为的简化

在需要「保持行为的简化」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:ce-simplify-code 在相同向量约束下，查找重复的长度计算。`

**预期结果与边界**：提出或实施最小化简，保留对外契约并重新运行测试。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：CE，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/ce-simplify-code/SKILL.md)。
