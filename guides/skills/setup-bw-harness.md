# setup-bw-harness：给项目接入工作约定

从业务目录显式调用。先查哪份指令生效、是否已有文档根与 Git 历史，再按项目实际情况合并。不为已有工程更换架构，也不为零术语的新工程创建词表。

| Pi 输入 | 看什么结果 |
|---|---|
| `/skill:setup-bw-harness check` | 真实路径、缺口和冲突；工作树、索引不变。 |
| `/skill:setup-bw-harness 接入这里，用本地计划` | 先展示选择，读取随包模板，合并工作规则与真实状态，检查 Git 和忽略效果。 |
| `/skill:setup-bw-harness update` | 已识别的旧 BW 规则原位更新，自定义设置和注释保留；不重写业务文件。 |
| `/skill:setup-bw-harness migrate 检查旧领域记录` | 实质历史资料整理移交 [project-governance](project-governance.md)，不整份改名。 |

接入后检查实际的 已创建／已更新／已保留／阻塞／检查／下一步。无测试不能声称测试通过。日常选路用 [bw-help](bw-help.md)，不是每次重新接入。

执行依据：[setup-bw-harness 正文](../../skills/setup-bw-harness/SKILL.md) · Matt `6f7f783` 派生（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
