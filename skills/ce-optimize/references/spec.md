# 第 0 阶段：输入类型和优化规范

在第 0 阶段开始时阅读本文。它包含如何从目标描述中区分规范路径，以及如何在 CP-0 之前加载、构建或验证规范。它验证的模式是 `references/optimize-spec-schema.yaml` 和 `references/experiment-log-schema.yaml`。

**地平线：**在停止规则内值得进行另一次测量或实验时继续。开始串行直到测量结果可信。一旦停止标准成立就停止。

### 0.1 确定输入类型

检查输入是否为：
- **规范文件路径**（以`.yaml`或`.yml`结尾）：读取并验证它
- **优化目标的描述**：帮助用户交互式地创建规范

### 0.2 加载或创建规范

**如果提供规格文件：**
1. 阅读 YAML 规格文件。编排代理本地解析 YAML —— 没有 shell 脚本解析。
2. 根据 `references/optimize-spec-schema.yaml` 的 `validation_rules` 部分中的 **每条** 规则验证规范。该部分是有效规范要求的唯一事实来源。不要依赖记住的子集；诸如单例标题和专有资源要求之类的条件规则仅存在于此。
3. 如果任何规则失败，请报告具体失败并要求用户修复它们，然后再继续

**如果提供说明：**
1. 分析项目以了解可以衡量的内容。如果面试需要，`references/usage-guide.md` 有更长的开始提示形状。
2. **检测优化目标是定性的还是定量的。** 这决定了 `type: hard` 与 `type: judge`，并且是最重要的规格决策：

   **在以下情况下使用 `type: hard`**：
   - 该指标是一个标量，具有明确的“更好”方向
   - 该指标是客观可衡量的（构建时间、测试通过率、延迟、内存使用情况）
   - 不需要人为判断来评价“这个结果真的好吗？”
   - 示例：减少构建时间、增加测试覆盖率、减少 API 延迟、减小包大小

   如果用户指定了多个必须全部满足的硬成功条件（例如，本地墙上时间和CI关键路径和跑步时间），请将它们作为`role: required`放入`metric.objectives`中，并保留`metric.primary`作为排名键。没有 `metric.objectives` 的规范保持单一主要接受。如果每次评估都需要几分钟，则设置 `measurement.stability.mode: ladder` 并进行相对或配对比较以及无效界限；不要在每个探索性实验上都花费完整的确认协议。从 `references/example-expensive-benchmark-spec.yaml` 开始绘制该形状。

   **在以下情况下使用 `type: judge`**：
   - 输出的质量需要语义理解来评估
   - 人工审核员需要查看结果才能说“这更好”
   - 代理指标存在，但可能会产生误导（例如，“更多集群”并不意味着“更好的集群”）
   - 优化可能会产生纸面上看起来不错的退化解决方案
   - 示例：聚类质量、搜索相关性、摘要质量、代码可读性、UX 副本、推荐相关性

   **重要**：如果目标是定性的，**强烈推荐`type: judge`**。解释说，仅靠硬指标就能优化代理数量，而无需检查实际质量。向用户展示三层方法：
   - **退化门**（硬的、廉价的、快速的检查，彻底拒绝候选者）：捕获明显损坏的解决方案，例如“1 个集群中的所有项目”或“0% 覆盖率”。先跑。如果任何门失败，请跳过昂贵的判断步骤。
   - **LLM-as-judge**（实际优化目标）：样本输出，根据评分标准对其进行评分，汇总。这就是循环优化的内容。
   - **诊断**（记录，从未用于拒绝）：分布统计、计数、计时。这些有助于解释为什么裁判分数会改变。

   如果用户坚持使用 `type: hard` 作为定性目标，请继续，但警告结果可能会优化误导性代理。

   **有效性门的范例。** 只有当分数本身就是一种判断时，才需要一个人的输入。当客观测量主要数据（持续时间、大小、计数、固定案例的通过率）时，无需向用户询问任何内容：测量结果是其自身的基本事实，并且阶段 1 会自行构建快捷方式探测。当主要是一个判断（`type: judge`，或者代表用户否则会评价的质量的硬指标）时，使用项目已有的已知良好和已知不良输出（记录的故障、固定装置、文本目标的情况）并仅询问用户缺少的内容：他们会在顶部评分的一些输出和在底部的一些输出。没有任何贡献的用户不会被阻止；第一阶段运行它可以进行的探测，并在批准时将其余部分规定为限制。当目标是指令文本（技能、代理指令文件、角色、工具描述）时，请在继续之前阅读`references/text-targets.md`：评估集和假设移动与代码目标不同。

3. **设计采样策略**（对于`type: judge`）：

   指导用户定义分层抽样。关键问题是：“您需要检查输出空间的哪些部分的质量？”

   演练这些问题：
   - **一个“项目”是什么样的？**（集群、搜索结果页面、摘要等）
   - **什么是自然size/quality地层？**（例如，大簇、小簇和单簇）
   - **哪里最有可能出现质量故障？**（例如，非常大的集群可能是退化合并；单例可能是错过分组）
   - **总样本量是多少才能平衡成本与信号？**（默认值：30 个项目，根据输出量进行调整）

   用于聚类的分层抽样示例：
   ```yaml
   stratification:
     - bucket: "top_by_size"     # largest clusters: check for degenerate mega-clusters
       count: 10
     - bucket: "mid_range"       # middle of non-solo cluster size range: representative quality
       count: 10
     - bucket: "small_clusters"  # clusters with 2-3 items: check if connections are real
       count: 10
   singleton_sample: 15          # singletons: check for false negatives (items that should cluster)
   ```

   抽样策略是特定于领域的。对于搜索相关性，分层可能是“前 3 个结果”、“结果 4-10”、“尾部结果”。概括来说，分层可能是“短文档”、“长文档”、“多主题文档”。

   **当目标涉及覆盖范围时，单例评估至关重要。** 使用单例标准对单例进行采样可检查系统是否缺少明显的分组。

4. **设计标题**（对于`type: judge`）：

   帮助用户定义评分标准。一个好的标题：
   - 有 1-5 级（或类似），每个级别都有具体描述
   - 包括帮助诊断问题的补充字段（例如，`distinct_topics`、`outlier_count`）
   - 足够具体，两位评委会给出相似的分数
   - 不假设 bigger/more 更好。 “平均每簇 3 个项目”本身并没有好坏之分
   - 请求每个项目的 `feedback` 字符串（出了什么问题，如何解决）；法官模板需要它，第 3 阶段从中生成假设

   聚类示例：
   ```yaml
   rubric: |
     Rate this cluster 1-5:
     - 5: All items clearly about the same issue/feature
     - 4: Strong theme, minor outliers
     - 3: Related but covers 2-3 sub-topics that could reasonably be split
     - 2: Weak connection: items share superficial similarity only
     - 1: Unrelated items grouped together
     Also report: distinct_topics (integer), outlier_count (integer)
   ```

5. 引导用户完成其余的规范字段：
   - 哪些不良案件应该被驳回？ （简并门，例如“solo_pct <= 0.95”捕获所有单子，“max_cluster_size <= 500”捕获巨型集群）
   - 什么命令运行测量？
   - 哪些文件可以修改？什么是不变的？
   - 有任何约束或依赖性吗？
   - 如果这是第一次运行：推荐`execution.mode: serial`、`execution.max_concurrent: 1`、`stopping.max_iterations: 4`和`stopping.max_hours: 1`
   - 如果用户指定了多个所需的硬目标或昂贵的宿主：如上所述推荐`metric.objectives`加`stability.mode: ladder`，并显示`references/example-expensive-benchmark-spec.yaml`
   - 如果`type: judge`：推荐`sample_size: 10`、`batch_size: 5`和`max_total_cost_usd: 5`，直到评分细则和宿主可信
   - Holdout：循环确认但从不选择的保留集。 `measurement.holdout.command`（与测量命令相同的JSON形状），或者对于与`sample_seed`不同的判断主`metric.judge.confirmation_seed`，其样本与选择样本不共享任何项目。 `type: judge` 以及运行在回合结束后通过唤醒在滴答之间等待时所需（`references/persistence.md`、等待记录和滴答）；另有建议，并且在批准门处注明不存在
   - 如果`type: judge`：不要在这里要求手工评分的例子。当用户已有标记样本时，将其命名为`metric.judge.calibration.labels`；否则保留其未设置状态，一旦判断了基线，第一阶段将提供简短的指导检查（`references/measurement.md` 1.3）
   - 每个案例的结果：当宿主可以发出 `cases` 映射（案例 ID 为 pass/fail）时，设置 `measurement.per_case: true` 并保留基线通过而候选失败的情况的总结报告
6. 将规范写入`<state-root>/spec.yaml`，其中`<state-root>`由`references/persistence.md`（状态根）解析
7. 在继续之前展示建议的范围、行为约束、测量方法和限制以供批准，并提供指向已保存规范的链接。应用SKILL.md主体面向用户的报告规则。将要求用户判断的任何内容放在他们面前：对于判断主要来说，这是标题的规模，逐级，因为这是他们对更好的定义，他们无法通过文件链接批准它。将所有这些内容作为普通消息发送，并进行布局以便于阅读（范围作为列表，范围和限制在各自的行中），然后才询问。问题本身是一个短句子及其选项：问题选择器将长文本显示为单个狭窄的块。
