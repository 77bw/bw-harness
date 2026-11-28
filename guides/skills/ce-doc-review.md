# ce-doc-review：实施前发现计划里没说清的验收条件

计划写着“支持中文和超长消息”，开发者仍不知道限制是 255 个字符还是 255 个字节。这种歧义应该在实施前找出来，而不是等代码写完再返工。

假设你的计划是 `docs/plans/frame-codec.md`，在 Pi 输入：

```text
/skill:ce-doc-review docs/plans/frame-codec.md 检查长度单位、超限行为和测试预期是否一致。只报告问题，不改计划。
```

换成真实文档路径。让审查列出矛盾的段落、为什么会产生两种实现，以及解决它所需的最小决定。有明确答案后更新**同一份**计划，未解决的业务选择交还给你。通过文档审查只意味着计划更可实施，不代表代码或测试已经通过。

执行依据：[ce-doc-review 正文](../../skills/ce-doc-review/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
