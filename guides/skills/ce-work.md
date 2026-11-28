# ce-work：实施已有计划并交付

目标和验收已经确定时，输入 `/skill:ce-work docs/plans/frame-codec.md`，把示例换成真实计划路径。原因未明的故障先用 [ce-debug](ce-debug.md)，只有目标没有可实施范围时先用 [ce-plan](ce-plan.md)。

在有历史的可写 checkout 上核对分支与原有工作中修改。按单元实施和提交，用真实验证与审查收据进入原生交付。检查报告中的变更、测试、审查、Git 修订及实际 PR。没有可用远端就区分本地完成和远程未交付。原生 `mode:return-to-caller` 用于已有调用方接管后续，不是禁用提交。参见[从计划到交付](../workflows/git-delivery.md)。

执行依据：[ce-work 正文](../../skills/ce-work/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
