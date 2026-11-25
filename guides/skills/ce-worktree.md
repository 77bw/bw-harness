# ce-worktree：隔离工作区

在需要「隔离工作区」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:ce-worktree 解释当前任务是否需要一个独立 worktree，先不要创建。`

**预期结果与边界**：只在明确授权后改 Git 分支和工作树；不作为新项目默认步骤。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：CE，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/ce-worktree/SKILL.md)。
