# ce-resolve-pr-feedback：判断、修复并核实已有评审反馈

已有可访问的 PR、具体讨论和对应 checkout。尚无人评审时应先运行 ce-code-review。

Pi 示例：`/skill:ce-resolve-pr-feedback 对当前 PR 的反馈逐条按代码和测试判断，修复成立的问题，区分本地解决与已发布。`

核对修订、测试、远端评论和讨论状态。只有发布并核实了的批次才可报告远端处理完毕。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[ce-resolve-pr-feedback 正文](../../skills/ce-resolve-pr-feedback/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
