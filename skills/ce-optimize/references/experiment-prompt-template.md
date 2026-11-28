# 实验工作人员提示模板

编排器使用此模板将每个实验分派给子代理或Codex。变量替换槽在生成时被填充。

---

## 模板

```
你是一名优化实验工作者。

您的工作是实施一个假设来改善可衡量的结果。您将在定义的范围内修改代码，然后停止。您无需运行测量工具、提交更改或评估结果——编排器会处理所有这些。

<experiment-context>
实验：#{iteration} 优化目标：{spec_name}
假设：{hypothesis_description}
类别：{hypothesis_category}

Current best metrics:
{current_best_metrics}

基线指标（任何优化之前）：
{baseline_metrics}
</experiment-context>

<scope-rules>
您可以修改这些路径中的文件：
{scope_mutable}

您不得修改这些路径中的文件：
{scope_immutable}

关键：不要修改可变范围之外的任何文件。测量工具和评估数据是不可变的，这意味着指标不能改变，而不是不能被操纵：除了完成指标所代表的工作之外的任何收益，或者打破下面的约束的收益，无论得分如何，都会被协调器恢复。
</scope-rules>

<constraints>
{constraints}
</constraints>

<approved-dependencies>
您可以添加或使用这些依赖项，无需进一步批准：
{approved_dependencies}

如果您的实现需要此列表中没有的依赖项，请停止并在输出中记下它。不要安装未经批准的依赖项。
</approved-dependencies>

<source-digest>
关于该目标所涉及的材料和当前的方法，您需要了解以下内容：

{source_digest}
</source-digest>

<failure-evidence>
当前最好的情况中最坏的情况与这一假设有关，以及出了什么问题。使用它们来检查您的更改是否存在真正的失败。假设仍然决定你实现什么，它可能会取代方法而不是修复这些情况：

{failure_cases}
</failure-evidence>

<previous-experiments>
最近的实验及其结果（作为上下文 - 避免重新尝试已经失败的方法）：

{recent_experiment_summaries}
</previous-experiments>

<instructions>
1. 读取您的更改涉及的可变文件。其余材料依赖源摘要，仅当假设依赖于摘要缺少的细节时才打开其他文件
2. 实现上述假设
3. 让您的更改集中且最小化——仅更改该假设所需的内容
4. 不要运行测量工具（协调器处理这个）
5. 不要提交（如果实验成功，编排器将在合并之前提交获胜的差异）
6. 不要修改可变范围之外的文件
7. 完成后，运行 `git diff --stat` 以便编排器可以看到您的更改
8. 如果您发现需要未经批准的依赖项，请记下并停止

专注于很好地实现假设。协调者将测量和评估结果。
</instructions>
```

## `execution.backend: remote` 的 Delta：测量和报告

远程工作人员在自己的机器上有自己的结帐，因此编排器无法测量其树。将此块附加到上面的模板（在同一提示内）并用它替换模板的指令 4（“不要运行测量工具”）。模板中的其他内容没有变化：范围、约束和依赖关系规则是相同的。

```
<remote-worker>
您正在独立运行，自行结账。协调器不会看到你的树；它只看到您推送的分支和您报告的结果。

基础：在分支{optimization_branch}上提交{base_sha}。在更改任何内容之前，请验证您的 HEAD 是否恰好是 {base_sha}。如果不是，请检查一下；如果你做不到，请停止并报告。

实现假设后，使用不可变的宿主按原样测量这台机器上的 PAIRED：
1. 基线：检查 {base_sha} （存储或分支您的更改），运行 `{measurement_command}` {sample_count} 次，记录每个样本。
2. 候选人：恢复您的更改，运行相同的命令相同的次数，记录每个样本。
当 {sample_count} > 1 时，备用基线和候选运行。切勿编辑测量命令、其工作目录或不可变范围内的任何文件；更换宿主会使您的结果无法使用。

使用消息 `optimize({spec_name}): exp-{iteration} <hypothesis, short>` 提交您的可变范围更改，而不做其他任何事情。该提交是候选者；它的 SHA 是 `head_sha`。

然后在结帐的存储库根目录中写入 `result.yaml` ，形状如下：
  实验：{iteration}
  base_sha: {base_sha}
  head_sha：<候选提交的 SHA>
  机器：<该机器或工人的稳定标识符>
  measured_at: <ISO 8601>
  基线：{ 门：{...}，指标：{ <name>：{ 聚合：<n>，样本：[...] } }，诊断：{...} }
  候选：{ 门：{...}，指标：{ <name>：{ 聚合：<n>，样本：[...] } }，诊断：{...} }
  正确性：<检查您运行的结果及其结果，或“无”>
仅当宿主发出时，才在每个快照中包含宿主的每个案例 `cases` 对象以及任何成本、令牌或延迟字段；不要自己计算它们。
在候选提交之上单独提交`result.yaml`，因此推送的提示的父级是`head_sha`，并推送到`{result_ref}`。不要推送到 {optimization_branch} 或任何其他分支。

您的最终消息是结构化结果：推送的 ref、head_sha、机器和两个聚合。报告未经批准的依赖项、碱基不匹配或无法作为阻塞项而不是结果运行的工具。
</remote-worker>
```

工人的数字是其自己的说法。编排器在配对快照上运行 `decide.mjs`，并在任何保留之前获取工作人员未生成的确认测量 (`references/loop.md` 3.4)。

## 变量引用

| 多变的 | 来源 | 描述 |
|----------|--------|-------------|
| `{iteration}` | 实验计数器 | 连续实验数 |
| `{spec_name}` | 规格文件`name`字段 | 优化目标标识符 |
| `{hypothesis_description}` | 假设积压 | 这个实验应该尝试什么 |
| `{hypothesis_category}` | 假设积压 | 类别（信号提取、算法等） |
| `{current_best_metrics}` | 实验日志`best`部分 | 当前最佳指标值（紧凑YAML或键：值对） |
| `{baseline_metrics}` | 实验日志`baseline`部分 | 任何优化之前的原始基线 |
| `{scope_mutable}` | 规格`scope.mutable` | 工人可以修改的files/dirs列表 |
| `{scope_immutable}` | 规格`scope.immutable` | 工人不得触摸的files/dirs清单 |
| `{constraints}` | 规格`constraints` | 要遵循的自由文本约束 |
| `{approved_dependencies}` | 规格`dependencies.approved` | 批准使用的依赖项 |
| `{source_digest}` | `source-digest.md` 在运行的临时目录中 | 工作人员需要了解目标的材料和当前方法的哪些内容 |
| `{failure_cases}` | `worst_cases` 当前最佳（保留实验条目或基线） | 与该假设相关的案例，并附上理由；缺席时“无记录” |
| `{recent_experiment_summaries}` | 实验日志中的滚动窗口（最后 10 个） | 紧凑的总结：假设、结果、经验教训 |
| `{base_sha}`（仅限远程） | 交付时`git rev-parse optimize/<spec-name>` | 工作人员必须从提交开始并作为基线进行衡量 |
| `{optimization_branch}`（仅限远程） | `optimize/<spec-name>` | 命名是为了让工人知道什么不该推动 |
| `{result_ref}`（仅限远程） | `optimize-exp/<spec-name>/exp-<NNN>` | 工人推的分支；协调器获取它来收集 |
| `{measurement_command}`（仅限远程） | 规格 `measurement.command` (+ `working_directory`) | 逐字运行；宿主是不可变的 |
| `{sample_count}`（仅限远程） | `1`对于`ladder`模式下的探索对； `repeat_count` 为 `repeat`； `1` `stable` | 每侧成对样品； `decide.mjs` 可能会通过后续调度要求更多 |

## 笔记

- 该模板适用于子代理、Codex和远程调度。没有特定于平台的假设。仅 `remote` 附加测量和报告增量。
- 对于 Codex 调度：将填充的模板写入临时文件并通过 stdin (`cat /tmp/optimize-exp-XXXXX.txt | codex exec --skip-git-repo-check - 2>&1`) 进行管道传输。
- 对于子代理调度：将填充的模板作为子代理提示传递。
- 保持`{recent_experiment_summaries}`简洁——每个实验 2-3 行，仅最后 10 行。不要包含完整的实验日志。
- 工作人员不应阅读完整的实验日志或策略摘要。它仅接收协调器提供的内容。
