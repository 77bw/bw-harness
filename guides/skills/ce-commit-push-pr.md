# ce-commit-push-pr：将已验证的变更交付成 PR

准备好功能分支、目标远端、认证和验证上下文；不是解决未知故障的入口。也支持只写 PR 描述的请求。

Pi 示例：`/skill:ce-commit-push-pr 将已审查的窗口修复推到当前测试远端并创建 PR，写上实际测试和审查依据，保留无关 WIP。`

核对目标/base、远端分支、实际 PR URL 和 CI；有反馈时交 ce-resolve-pr-feedback。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[ce-commit-push-pr 正文](../../skills/ce-commit-push-pr/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
