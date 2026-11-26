# ce-test-browser：验证变更实际影响的页面

从分支或指定 PR 确认受影响路由及本地开发服务器。纯逻辑库没有页面时，如实报告不适用；不要替代独立算法向量。

Pi 示例：`/skill:ce-test-browser 对当前分支受影响的搜索页执行浏览器测试；记录实际端口、交互、错误与没有覆盖的第三方认证。`

核对真实页面、交互与通过／失败／跳过结果；外部账户验证留给相应参与者。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[ce-test-browser 正文](../../skills/ce-test-browser/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
