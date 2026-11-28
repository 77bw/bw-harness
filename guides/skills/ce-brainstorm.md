# ce-brainstorm：先选要解决的问题，不急着定接口

“加流式解码”可能是要从文件读连续帧，也可能只是要更好地报告截断。两种需求牵涉的用户行为不同；在这里讨论的是**要做什么**，还不是怎么实现。

`/skill:ce-brainstorm 我的离线工具读到半个帧就报错。请先和我比较“报告截断”和“等待更多输入”两种需求，确认用户、非目标和验收例子。`

给它实际使用场景和不能改变的约束。把选定范围保存在 `docs/plans/` 的需求级计划，随后由 [ce-plan](ce-plan.md) 延展，而不是再写一份平行 spec。若两种方案的差别必须亲自操作才看得清，可转 [ce-prototype](ce-prototype.md)；若“如何处理半帧”早已定好，跳过探索。

执行依据：[ce-brainstorm 正文](../../skills/ce-brainstorm/SKILL.md) · CE `fcb5e3a`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
