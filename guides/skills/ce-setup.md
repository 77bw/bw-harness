# ce-setup：检查 CE 配置

在需要「检查 CE 配置」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:ce-setup 只检查当前项目 docs_root 的来源，不安装额外工具或修复配置。`

**预期结果与边界**：报告原生健康状态，修改配置先审查；通常由统一 setup 承接。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：CE，修订与导入范围见 [上游锁](../../upstream.lock.yml)。[运行说明及依赖资源](../../skills/ce-setup/SKILL.md)。
