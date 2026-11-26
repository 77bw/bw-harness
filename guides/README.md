# BW Harness 使用手册

第一次使用？从[快速上手](quick-start.md)在自己的目录生成一个可导入的 Python 包。已经有源码？直接看[接手已有项目](workflows/existing-project.md)，不要在原目录执行 `new`。

```text
装一次包 → 每个新项目初始化一次
           ↓
      说清功能和术语 → 把决定写成计划 → 实施、测试和审查
                                            ↓
                                  更新状态，必要时沉淀经验
```

这不是每次都要走的流水线。修一处明确的错误，可以从失败用例开始；发现旧文档与代码不符，可以只检查，不必改代码。

## 按手头的事选路线

| 你现在要做什么 | 从这里开始 | 结束时看什么 |
|---|---|---|
| 开新项目，做第一个功能 | [新项目](workflows/new-project.md) | 一个计划、一组真实测试，不是只有目录 |
| 接手旧工程，不想覆盖原有文件 | [已有项目](workflows/existing-project.md) | 只读清单、获准批次和前后基线 |
| 比较候选算法，决定哪个能进正式包 | [算法开发](workflows/algorithm-development.md) | 独立测试向量、可复现实验 |
| 修复一个能描述的失败 | [Bug 修复](workflows/bug-fixing.md) | 可区分原因的失败用例和回归结果 |
| 刚解决了一个容易再踩的坑 | [知识沉淀](workflows/knowledge-compounding.md) | 测试、标准或已有经验的更新 |
| 新会话不想从头探索 | [接续](workflows/session-recovery.md) | 可核对的状态和一个下一步 |

包没加载看[安装](installation.md)和[排错](troubleshooting.md)。不知道某个文件该放哪里，分别查[项目结构](project-structure.md)和[文档职责](document-structure.md)。

## Skill 速查

表中链接均为独立指南，示例在 **Pi 对话里**输入。BW 自研三个入口；领域建模和设计工具来自 Matt Pocock，`ce-` 开头的来自 Compound Engineering。详细修订见[上游锁](../upstream.lock.yml)。不需要记住全部名字。

| 主入口和常用流程 | 什么时候选 |
|---|---|
| [setup-bw-harness](skills/setup-bw-harness.md) / [bw-help](skills/bw-help.md) | 初始化或检查项目 / 只问下一步怎么走 |
| [grill-with-docs](skills/grill-with-docs.md) / [ce-brainstorm](skills/ce-brainstorm.md) | 术语、业务边界不清 / 产品需求和范围未定 |
| [ce-plan](skills/ce-plan.md) / [ce-work](skills/ce-work.md) | 已定目标要变成计划 / 已有计划要实施 |
| [project-governance](skills/project-governance.md) / [ce-compound](skills/ce-compound.md) | 检查、迁移、收尾 / 留下已证实的经验 |

| 按需要调用，不属于默认步骤 | 怎么选 |
|---|---|
| [ce-ideate](skills/ce-ideate.md)、[ce-bakeoff](skills/ce-bakeoff.md)、[ce-pov](skills/ce-pov.md) | 找方向 / 展开候选方案再比 / 对已给出的方案做判断 |
| [ce-explain](skills/ce-explain.md)、[ce-prototype](skills/ce-prototype.md) | 弄懂现有行为 / 亲自试用原型才能决策 |
| [tdd](skills/tdd.md)、[ce-debug](skills/ce-debug.md)、[ce-optimize](skills/ce-optimize.md) | 测试先行 / 定位失败 / 用测量改进性能 |
| [improve-codebase-architecture](skills/improve-codebase-architecture.md)、[ce-simplify-code](skills/ce-simplify-code.md) | 寻找值得重划的模块 / 行为不变，简化已知变更 |
| [ce-doc-review](skills/ce-doc-review.md)、[ce-code-review](skills/ce-code-review.md) | 查计划的验收缺口 / 查代码变更的风险 |
| [ce-handoff](skills/ce-handoff.md)、[ce-worktree](skills/ce-worktree.md) | 显式交接 / 经授权隔离 Git 工作区 |

**通常由其他 Skill 带入：** [grilling](skills/grilling.md) 逐问决策，[domain-modeling](skills/domain-modeling.md) 维护领域语言，[codebase-design](skills/codebase-design.md) 对齐模块设计，[ce-noslop](skills/ce-noslop.md) 清理文案，[ce-setup](skills/ce-setup.md) 检查 CE 自身配置。旧流程中的 [ce-compound-refresh](skills/ce-compound-refresh.md) 是兼容入口，不是第二套知识系统。
