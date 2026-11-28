# improve-codebase-architecture：先找值得改的边界，再选一处深入

项目扩大后，路由、CLI 和编码函数都在检查同一个长度字段。一次把所有目录重排风险很大；先让 Agent 找出重复知识出现在哪些调用点。

`/skill:improve-codebase-architecture 检查 CLI 和 API 是否各自实现了长度规则。给我候选改进和相应源码位置，先不要重构业务代码。`

给它可读取的工程与术语表。上游会把候选整理成可视化 HTML 报告；这是**报告文件**，不是代码变更，先确认允许的落点。你选中一个候选后再讨论接口和取舍，必要时记录决策。若只是某个函数里有重复分支，不必做全项目扫描，用 [ce-simplify-code](ce-simplify-code.md) 更直接。
