# 管道模式（`mode:pipeline`）

相同的报价引擎，每个委托和路线都有一份剩余合约：

1. **委托以非交互方式运行。** 调用 `ce-resolve-pr-feedback mode:pipeline` 进行评论，调用 `ce-debug mode:pipeline` 进行CI；收集他们的结构化结果。永远不要询问用户任何事情。
2. **一个持久的决策集。** 每个返回的类型化 `needs-human` 残差都以不变的方式输入到一个 `human_decisions` 记录中，并具有稳定的 `decision_id` 及其完整 `sources` 集的精确观测值。快照为调用者派生规范的 `needs_human_residuals` 列表。更改或缺失的观察结果会使整个决定无效，并使幸存的来源再次可操作；只有`mark --answer-decision <decision_id> --answer-file <path>`记录人类答案并重新激活未更改的源。没有完整有效负载的决策是可操作的工作，永远不会被覆盖。渲染`## Needs your decision`下的集合；保持其评论线程开放。任何没有线程主目录的内容也会进入一个运行报告 PR 注释，而不是 PR 正文。
3. **有界停止，从该集合派生。**继续每个仍然可以自主进展的独立流。一旦没有剩余，当`needs_human_residuals`非空时立即返回`status: "needs-human"`；仅当集合为空且满足以下干净状态条件时才返回成功；否则返回固定、回合或时间预算并带有残差。永远不要等待人工输入、人工批准或合并就绪的结算窗口。

旧的PR摄入返工或关闭判决在第一个快照之前返回，形状为`references/intake.md`定义；更新判决持续到这些时间点并且永远不会重写历史。

终端但红色的支票、竞赛、待处理或未经验证的当前基础身份、未知或非干净的合并状态（`update_branch_at_merge`除外）、经理过时或未知的目标、open/claimed/parked当前货币项目或PR创建后的空`statusCheckRollup`是残差，而不是通行证。在`posture:stack-land`下，当成功门成立时，在将该层视为管道成功或前进之前执行步骤3的stack-land land步骤。刚刚落地的 MERGED 结果会继续下一个开放的非草案PR需要工作的管道，而不是结束调用。

## 管道停止

**在 `mode:pipeline` 中，一旦没有可操作的积压，就使用有界管道停止**。仅当`needs_human_residuals`为空、`all_checks_ok`、`mergeability_certain`、`merge_state_status == "CLEAN"`或`update_branch_at_merge`、`base_ref_blocker`、`stack_blocker`为空、`branch_currency_blocker`为空、`unrequested_base_merge`为空时报告成功。 `update_branch_at_merge` 成功告诉调用者分支在合并时必须更新。没有自主工作的非空规范集立即返回`{ status: "needs-human", checks_terminal, fixes_applied, residuals: needs_human_residuals }`。否则，继续工作独立流，直到它们清除或预算结束运行并产生剩余。终端和阻塞条件仍然适用。

无论哪个停止产生它，结构化结果都是该技能写入的最后内容。它结束了该技能，而不是回合。控制权在同一会话中返回给调用者，调用者自己对结果的处理决定其运行是继续还是停止。
