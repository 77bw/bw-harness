# project-governance：结构治理

在需要「结构治理」时使用。先读取当前项目约束与相关测试，不代替用户的写入授权。

Pi 场景示例：`/skill:project-governance check：列出根目录临时脚本及被跟踪的 .local 文件。`

**预期结果与边界**：按路径给诊断；close 在回归后更新 status，migrate 需逐批批准。

找不到入口时先查[安装与冲突](../installation.md)，不要安装第二份同名插件。Claude/Codex 调用状态见该页；此示例不是跨宿主验收记录。

来源：BW 自研。[运行说明及依赖资源](../../skills/project-governance/SKILL.md)。
