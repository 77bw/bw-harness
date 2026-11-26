# ce-handoff：把当前会话交给读不到这段对话的人

`docs/status.md` 已经说明进展，但下一位开发者还需要知道“为什么不采用字符数”和“哪个测试仍未运行”。此时可以额外交一份短索引，不必导出整个会话。

`/skill:ce-handoff create 下一位只需复验截断输入：指向当前计划、ADR 和测试，区分已验证与待验证，不附原始数据。`

`create` 会写交接文件。默认托管位置是临时存储，可能被系统清理；看最终路径、保留期限和访问限制。新会话用 `/skill:ce-handoff resume` 加**实际返回的文件路径**。这一步只授权读取交接并定位，不是授权执行文中所有命令。普通同仓库接续，直接读 status 和计划就够了。

执行依据：[ce-handoff 正文](../../skills/ce-handoff/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
