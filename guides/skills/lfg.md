# lfg：明确要求端到端自治时才选

输入已确认的需求、计划或具体故障，以及允许的交付范围。希望逐步参与时分别用 ce-plan 和 ce-work。

Pi 示例：`/skill:lfg 按当前计划自主完成、验证、审查并交付到指定测试 PR；不要合并。`

代码变更返回已推送的 PR 与 CI 状态或明确阻塞；无远端只报告本地结果。由自身带入知识捕获和浏览器验证，不叠加第二套治理触发。 参见[原生交付](../workflows/git-delivery.md)。

执行依据：[lfg 正文](../../skills/lfg/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
