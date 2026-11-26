# ce-work：拿着一个确定的计划实施

适用于“做什么、怎样验收”已经清楚的工作。若只有一个报错而不知道原因，先用 [ce-debug](ce-debug.md)，不要让实施流程猜根因。

以下假设计划位于 `docs/plans/frame-codec.md`，使用时换成项目里真实存在的路径：

```text
/skill:ce-work mode:return-to-caller docs/plans/frame-codec.md 仅本地实施与验证，不暂存、不提交、不推送。若所选执行路径需要 Git 写入，停止该路径并告诉我。
```

它可以改 `src/` 和 `tests/`，也可以返回阻塞。`return-to-caller` 的含义是**由调用方接手收尾**，不是对所有内部 Git 行为的技术封锁。原生方式不适合当前权限时，明确授权受控本地实施，不悄悄放宽约束。

拿到结果后分别看变更文件、实际运行的测试、未验证项。跳过交付尾部也意味着不能假设最终审查已经发生；按需要请 [ce-code-review](ce-code-review.md) 独立检查，再做治理。
