# ce-setup：诊断 CE 自身工具与仓库配置

`/skill:ce-setup 只检查当前项目的配置，告诉我 docs_root 来自哪个文件、计划应写到哪里；不要修复或安装。` 适用于 CE 产物位置或原生工具有问题，不是接入整个 BW 工作流的必经步骤。

报告应分清没有配置、配置不合法和工具不可用；需要修复时确认具体建议，不整份覆盖已有配置。共享配置中的非法根应先修复，不把计划写到猜测的位置。第一次接入整个项目用 [setup-bw-harness](setup-bw-harness.md)。

执行依据：[ce-setup 正文](../../skills/ce-setup/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
