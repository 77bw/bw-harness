# 支币（第三流）

分支货币仅用于消费：仅针对快照发出的确切 `branch_currency` 项进行从基到头的更新，并且此步骤永远不会创建自己的项。没有项目意味着没有从碱基到头部的突变，无论其他移动。

**谁更新了 `BEHIND` 分支。** GitHub 仅当基础要求分支在合并前保持最新时才报告 `BEHIND`，因此每个基础移动都会再次报告它，并且只有在合并之前进行的更新才算在内。在 `target` 和 `stack-ready` 下，此运行永远不会合并，因此无论谁合并都会更新分支：在每个 `snapshot` 和 `watch` 上传递 `--defer-behind-to-merge`，同时保持该姿势。然后，快照不会发出 `BEHIND` 项目，而是报告 `update_branch_at_merge`； `references/settle.md` 接受代替 `CLEAN` 和 `references/report.md` 告诉用户在合并时更新分支。省略 `stack-land` 下的标志或当用户要求保持分支当前时，因此 `BEHIND` 项在下面发出并消耗。缺少标志只需要额外 CI 运行，绝不会出现错误就绪。 `DIRTY`在任何姿势下都不受旗帜影响。

6. **分支货币和冲突（第三个流 - 在评论和 CI 之后）。** 对当前的 `branch_currency` 项目执行操作；永远不要从合并状态的散文中推断出新项目。 `UNKNOWN` 可合并性或任何非空 `base_ref_blocker` 不会产生任何项目，并且只会重新轮询。托管堆栈和 `probe-error` 不包括在此步骤中。对于独立的 PR 或符合条件的手动依赖项，`normal-base` 项可能是目标本地的；不要将手动依赖项重定向到其父级。开放子依赖项不会取消根PR的资格，但是此步骤永远不会重写、变基或改变依赖头。
   - **检查和索赔生命周期。** 当快照使分组决策无效时，货币来源仍然携带其普通的突变安全事实；像往常一样应用它们。如果`attention == "decide"`，则通过共享的`--residual-file`标记返回确切的货币来源作为键入的`needs-human`残差（相同的记录审核和CI使用）并且不认领它；只有完全匹配的记录答案才能授权另一个突变。如果`attention == "inspect"`，首先预览当前冲突并计算其语义冲突指纹。与`parked_semantic_fingerprints`比较，然后用`--currency-inspected-fingerprint <fingerprint>`标记确切的项目。未改变的证据仍保留；更改后的证据将使旧公园退役并重新开放该项目。在检查通过之前请勿提出索赔。对于 `attention == "claim"`，并且仅在保留固定预算的情况下，在任何外部突变或本地合并开始之前以原子方式标记确切的项目**：

     ```bash
     SKILL_DIR="<absolute path of this skill's directory>"; STATE_DIR="<the $STATE_DIR resolved above: $SCRATCH_ROOT/ce-babysit-pr/<host>-<owner>-<repo>-<N>>"; RUN_INVOCATION_ID="<invocation_id>"; RUN_STARTED_AT="<invocation_started_at>"; RUN_BUDGET_SECONDS="<invocation_budget_seconds>";
     PY="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1 && { echo "$c"; break; }; done)"; [ -n "$PY" ] || { echo "no working Python 3 interpreter on PATH" >&2; exit 1; };
     "$PY" "$SKILL_DIR/scripts/pr-snapshot" mark --state-dir "$STATE_DIR" --invocation-id "$RUN_INVOCATION_ID" --session-started-at "$RUN_STARTED_AT" --invocation-budget-seconds "$RUN_BUDGET_SECONDS" --currency-key <currency_key> --currency-disposition claimed
     ```

     重新进入`claimed`仅用于调节：检查远程和本地证据，切勿直接重新提交。准确记录 `--currency-outcome mutation-observed`、`--currency-outcome proven-no-mutation` 或 `--currency-outcome ambiguous` 之一。仅通过恢复记录的结果保持安全来继续自主：协调观察到的突变以进行确认。只有在确凿的无突变证明和引擎退避之后才可能进行一次重试。不明确的结果永远不会重试或重新提交。对照相同的`--currency-key`进行确认。每个没有安全自主延续的终端货币结果都会在同一个锁定命令中记录一个完整的类型残差，其中源为`{ id: <currency_key>, kind: "currency" }`，直到`--residual-file`。这将创建与审核和 CI 使用的相同决策记录；货币没有单独的停放或应答决策状态。通过 `tick.md` 中共享的 `--answer-decision <decision_id> --answer-file <path>` 转换获取人类答案，然后根据重新激活的精确观察采取行动。过时的调用、耗尽的预算/`max-runtime`或声明和突变之间的head/base移动会在写入之前拒绝或使操作无效。
   - **`BEHIND`：仅限主机拥有的更新。** 仅针对 `route == "normal-base"` 和 `host_branch_update_capability == true` 继续； `false`/denied 或`unknown` 是`needs-human` 路径，从未从Git 或直推权限推断。声明后，立即重新验证远程头和基础 OID 是否仍等于观察结果。通过GitHub的`PUT /repos/{owner}/{repo}/pulls/{number}/update-branch`端点调用主机更新操作一次，并将`expected_head_sha`设置为声明的观察的头SHA；切勿使用无法传输该先决条件的更新助手。将 HTTP 422 头不匹配视为过时声明：重新快照并协调，无需重新提交。宿主接受度为`mutation-observed`，未完成。只有在新的快照和祖先证据证明生成的头包含其观察到的基本 OID 并且没有不相关的 head/base 移动或不同的当前货币证据使该证明无效后，才能确认所声称的确切观察结果。所声明的物品自己的`branch_currency_blocker`将保留到确认为止，并且不需要事先为空。仅仅移动头部并不能证明这一点。
   - **`DIRTY`：仅限精确基本地修复。** `host_branch_update_capability` 不相关，并不意味着推送访问。单独证明，无需变异，普通直接推送权限到确切的 head ref；未知或被拒绝的权限需要上面的共享类型决策。需要在观察的头部进行经过验证的干净PR头签出，获取准确的观察到的基本OID，并运行非变异合并预览。语义冲突指纹是排序后的冲突路径加上它们的阶段 blob 标识；它排除了基础 OID，因此不相关的后续基础移动无法掩盖相同的冲突。仅在具有**积极意图证据**并且**没有合理的替代行为**的情况下，解决方案才是机械的。两个看似合理的解决方案、实质性行为或用户意图选择、范围不受限制、陈旧的 OID、不完整的证据或缺乏权威意味着安全中止并通过共享剩余标记、具体选项、权衡和精益的`--semantic-conflict-fingerprint <fingerprint>`。
   - **应用并确认机械 `DIRTY` 修复。** 声明并重新验证确切的 head/base OID，并再次清理签出，合并该确切的基本 OID，并在本地合并开始后立即标记 `--currency-outcome mutation-observed`。仅解决预览的机械冲突，按比例进行验证，并使用正常推送到精确的头部参考。切勿变基或强制推送。中断的本地合并必须与其经过验证的提交协调一致或在停放之前安全中止；切勿在其上进行第二次尝试。仅当远程证据证明头部等于或包含经过验证的合并提交、新快照清除了货币门并且没有不相关的移动使声明无效时才进行确认。 **单独的远程头部运动并不能证明或确认。**
   - **托管堆栈或探测不确定性。** 使用 `manager_status == "confirmed"`，管理器货币超越普通状态：预先存在的目标陈旧度变为 `stack-sync-needed`，绝不会采用此路线；第 7 步（托管堆栈维护）单独执行推送后管理器维护。对于经理或关系`probe-error`，继续review/CI，但不执行分支货币突变或就绪声明，直到分类成功。

## `unrequested_base_merge`（缺陷检测器）

当没有声明的货币项目生成它时，快照标记一个头，该头是基本提示的双父合并（`unrequested_base_merge: {head, base_parent}`；唤醒原因`unrequested-base-merge`）。这就是事件形状 - 主要移动，有人将其合并为 CLEAN PR，绿色 CI 重新启动 - 不是维护。在标记摘要中将其报告为缺陷残留，如果提交告诉您，请指出推送它的人，并继续观察。切勿通过变基或强制推送来撤消它，也切勿将生成的 `BLOCKED`-while-checks-rerun 视为新的阻塞项。它会在下一个头上自行清除。
