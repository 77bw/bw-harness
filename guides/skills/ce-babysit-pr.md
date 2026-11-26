# ce-babysit-pr：跟踪一个已经存在的 PR

需要在一段时间内关注开放 GitHub PR 的状态，先给出 PR 和看护范围；一次性处理现有评论用 ce-resolve-pr-feedback。

Pi 示例：`/skill:ce-babysit-pr 检查这个 PR 的 CI、评审与合入条件，使用 checkpoint 返回需要我决定的事项。`

看返回的远端状态和待处理项；没有运行或没有权限不等于 CI 已通过，不把看护视为自动合并许可。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[ce-babysit-pr 正文](../../skills/ce-babysit-pr/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
