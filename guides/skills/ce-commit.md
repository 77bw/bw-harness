# ce-commit：只把本次变更保存为本地提交

已有明确范围且只需要本地修订。先看差异、暂存区与无关 WIP；若要推送或开 PR，换用 ce-commit-push-pr。

Pi 示例：`/skill:ce-commit 只提交当前分支已核对的窗口边界修复，保留我未完成的文档编辑。`

检查实际提交哈希、包含的路径和留在工作树的内容；这一步不会产生远端 PR。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[ce-commit 正文](../../skills/ce-commit/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
