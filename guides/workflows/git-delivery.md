# 从现有计划走到 PR 与反馈

1. 从状态索引或用户给定路径找到**实际计划**。需要形成新计划才用 `/skill:ce-plan`；已有计划用 `/skill:ce-work` 加上该路径。若 CE 已在执行，按原生运行标识恢复，不启动第二次。
2. 让 CE 在功能分支上实施、按单元提交、执行项目验证、简化与独立审查。看报告中的实际命令、修订、审查收据和未处理项。`mode:return-to-caller` 是高级编排接口，不是关闭 Git 提交的开关。
3. 到完成检查点，有已验证的错误认识才由 Compound 判断如何捕获；治理核对结果和当前状态。若新测试或规则超出旧收据范围，先补受影响的验证和审查再交付。
4. 发布到指定远端时由 [ce-commit-push-pr](../skills/ce-commit-push-pr.md) 推送并创建 PR；若任务只需本地提交，则走 [ce-commit](../skills/ce-commit.md)。无可用远端时分别报告本地 commit 和远端缺项。用户本来的 WIP 不纳入本次提交。
5. 有新评审意见交给 [ce-resolve-pr-feedback](../skills/ce-resolve-pr-feedback.md)，需要跟踪已有 PR 时用 [ce-babysit-pr](../skills/ce-babysit-pr.md)。以远端实际分支、PR、CI 与讨论状态核实结果，不把“已建 PR”当作“已合并”。
