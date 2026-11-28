# 第 3 阶段：可选增强

### 第 3 阶段：可选增强

**等待第 2 阶段完成后再继续。**

此阶段仅是交互式的：非交互式调用者没有人在循环中对审查者的发现采取行动，并且下游自动化可以自行运行专门的审查者（如果他们想要通过）。

<parallel_tasks>

根据问题类型，可以选择从 `references/agents/` 调度使用本地提示资产播种的通用子代理来查看文档。不要在 type/name 之前派遣独立代理。

- **performance_issue** → `references/agents/performance-oracle.md`
- **security_issue** → `references/agents/security-sentinel.md`
- **database_issue** → `references/agents/data-integrity-guardian.md`
- 任何代码繁重的问题 → 将代码简化保留为**只读文档审查**。检查解决方案草稿的代码示例和内嵌的解释性声明，或者调度一个通用子代理，该子代理带有本地提示，仅返回建议。不要从这个阶段调用`ce-simplify-code`，也不要改变产品代码，除非用户明确要求单独的代码简化过程。不要使用已删除的`code-simplicity-reviewer`。
  示例：查看解决方案草案的示例，了解推测性抽象、冗余包装器、死分支和以防万一参数。仅将编辑应用于 `ce-compound` 正在写入的 documentation/examples；保持任何分支代码更改不变。

</parallel_tasks>

---

## 适用的专业本地提示

根据问题类型，这些本地提示资产可以增强文档记录：

### 代码质量和审查
- **只读代码简化审查**：检查解决方案示例和文档声明是否存在不必要的复杂性，而无需更改产品代码
- **references/agents/pattern-recognition-specialist.md**：识别反模式或重复问题

### 特定领域专家
- **references/agents/performance-oracle.md**：分析performance_issue类别解决方案
- **references/agents/security-sentinel.md**：审核security_issue漏洞解决方案
- **references/agents/data-integrity-guardian.md**：评论 database_issue 迁移和查询

### 增强与研究
- **references/agents/best-practices-researcher.md**：通过行业最佳实践丰富解决方案
- **references/agents/framework-docs-researcher.md**：指向 framework/library 文档参考的链接

### 何时调用
- **自动触发**（可选）：使用本地提示播种的通用子代理可以运行后期文档以进行增强
- **手动触发**：用户可以在`ce-compound`完成后运行`ce-simplify-code`等幸存技能，以进行更深入的代码审查和变异
