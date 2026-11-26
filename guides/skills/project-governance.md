# project-governance：检查、迁移、收尾

- **检查。** `/skill:project-governance check 核对当前计划链接和该主题的研究依据`。仅诊断，返回优先级、位置、证据、影响和建议，不写报告或状态。不把平铺项目或缺少可选文档误报为错。
- **迁移。** `/skill:project-governance migrate 请按段检查旧研究笔记，先列建议`。逐批确认源、目标、重复和冲突、受影响引用、证据与回退办法。只执行已经批准的批次；未知判断、唯一原样本和业务文件保留。
- **收尾。** `/skill:project-governance close 这项任务暂停。请核对当前计划、Git 和上次测试依据，记录失败处与下一步`。原位更新 status，按证据更新研究，不重复仍有效的原生审查或已完成的经验捕获。没有足够证据就返回部分完成或阻塞。

结果应清楚区分实际与建议、先前与本次验证。治理不是第二套代码审查或 Git 提交流程；新增测试或规则交还原生最终校验。[迁移示例](../workflows/existing-project.md)

执行依据：[project-governance 正文](../../skills/project-governance/SKILL.md) · BW v1.1.0 自研（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
