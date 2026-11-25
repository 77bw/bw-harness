# ce-code-review：审查变更

在需要「审查变更」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:ce-code-review 针对当前 diff 检查截断帧是否绕过边界校验，只报告发现。`

**预期结果与边界**：按影响和文件列出问题与测试盲区；审查结果不是自动发布许可。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：CE，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/ce-code-review/SKILL.md)。
