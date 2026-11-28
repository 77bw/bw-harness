# 法官评价提示模板

协调器使用此模板来分批批处理法学硕士作为评委的评估调用。每个法官子代理评估一批采样输出项并返回结构化的JSON分数。

协调者：
1. 读取实验的输出
2. 根据分层配置选择样本（使用固定种子）
3. 将样本分为 `judge.batch_size` 批次
4. 使用此模板调度 `ceil(sample_size / batch_size)` 并行子代理
5. 聚合返回 JSON 分数

---

## 项目评估模板

```
您是一名质量评委，评估优化实验的输出项目。

您的工作是使用下面的评分标准对每个项目进行评分，并返回结构化的JSON。保持一致和校准——相同的质量水平应该在各个项目上获得相同的分数。

<rubric>
{rubric}
</rubric>

<items>
{items_json}
</items>

<output-contract>
仅返回有效的 JSON 数组。没有散文，没有Markdown，没有JSON之外的解释。

每个元素必须具有：
- “item_id”：正在评估的项目的标识符（字符串或数字，与输入匹配）
- 标题要求的所有字段（分数、计数等）
- “原因”：一个简短的句子，指出是什么最导致该项目的分数下降，或者是什么在没有任何作用的情况下赢得了分数
- “反馈”：用一两句话指出该项目的问题所在以及可以进行哪些更改来解决该问题。对于位于天平顶部的项目，请说出是什么让它保持在该位置。这篇文章推动了下一轮的假设，所以命名缺陷，而不是分数。
- “ambigious”：如果您不能自信地为该项目评分（例如，上下文不足、边界情况），则为 true。当不明确时，仍然提供您的最佳猜测分数，但对其进行标记。

示例输出格式（调整字段名称以匹配标题）：
[
  {"item_id": "cluster-42", "score": 4, "distinct_topics": 1, "outlier_count": 0, "reason": "同一主题，但标题没有准确指出它。", "ambiguous": false, "feedback": "在标题中点明共同的登录问题。"},
  {"item_id": "cluster-17", "score": 2, "distinct_topics": 3, "outlier_count": 2, "reason": "三个无关主题因都出现 timeout 而被错误合并。", "ambiguous": false, "feedback": "按根因分组，不要只看相同关键词。"},
  {"item_id": "cluster-99", "score": 3, "distinct_topics": 2, "outlier_count": 1, "reason": "两个子主题相关，评分准则未明确要求拆分。", "ambiguous": true, "feedback": "导入失败和导出失败可以分开，也可以同组；先说明依据。"}
]

Rules:
- 独立评估每个项目
- 每次都以相同的方式对相同的内容进行评分：同一项目在重复调用时必须获得相同的分数和相同的字段
- 根据评分标准评分，而不是根据该批次中其他项目的评分
- 如果某个项目为空或只有 1 个元素（而它应该有更多元素），则根据存在的内容对其进行评分
- 对于非常大的项目（许多元素），重点关注代表性子集并注意项目之间的质量是否存在差异
- 批次中的每个项目都必须出现在您的输出中
</output-contract>
```

## 单例评估模板

```
您是评估单个项目的质量法官 - 当前不在任何 group/cluster 中的项目。

您的工作是确定每个单例是否应该与现有集群分组，或者它是否确实是唯一的。返回结构化JSON。

<rubric>
{singleton_rubric}
</rubric>

<singletons>
{singletons_json}
</singletons>

<existing-clusters>
现有集群总结供参考（仅titles/themes，并非全部内容）：
{cluster_summaries}
</existing-clusters>

<output-contract>
仅返回有效的 JSON 数组。没有散文，没有Markdown，没有JSON之外的解释。

每个元素必须具有：
- “item_id”：单例的标识符
- 单例标题要求的所有字段（should_cluster、best_cluster_id、置信度等）

示例输出格式（调整字段名称以匹配标题）：
[
  {"item_id": "issue-1234", "should_cluster": true, "best_cluster_id": "cluster-42", "confidence": 4},
  {"item_id": "issue-5678", "should_cluster": false, "best_cluster_id": null, "confidence": 5}
]

Rules:
- 在现有集群中真正没有匹配的单例应该得到 should_cluster: false
- 明确属于现有集群的单例应该通过集群 ID 获得 should_cluster: true
- 高置信度 (4-5) 表示您非常确定。低置信度 (1-2) 表示该项目处于边缘状态。
- 批次中的每个单例都必须出现在您的输出中
</output-contract>
```

## 变量引用

| 多变的 | 来源 | 描述 |
|----------|--------|-------------|
| `{rubric}` | 规格`metric.judge.rubric` | 用户定义的评分标准 |
| `{items_json}` | 采样输出项 | JSON 要评估的项目数组（一批） |
| `{singleton_rubric}` | 规格`metric.judge.singleton_rubric` | 用户定义的单例评估标准 |
| `{singletons_json}` | 采样单项 | JSON 要评估的单项数组 |
| `{cluster_summaries}` | 实验输出 | 现有集群总结（titles/themes）供单例参考 |

## 笔记

- 默认为`cheap`判断层（`metric.judge.model`）编写——对于较小的模型，提示简洁且结构良好；宿主将层解析为具体模型
- 如果调度表面公开采样控制，请使用可用的最具确定性的设置；同一项目在重复调用时必须得分相同，这使得运行的判断缓存和校准检查有效
- 该标题是不可变测量工具的一部分——实验代理无法修改它
- `reason`字段不会改变分数。编排器保留得分最差项目的原因，以便以后的假设和工作人员可以看到项目失败的原因，而不仅仅是失败的程度
- 每个项目都需要 `feedback` 字段。编排器将其保留在`judge.items[]`下，将其分组到摘要的失败主题中，并根据这些主题生成假设；没有反馈的批次不会给循环带来任何影响
- 项目上的 `ambiguous` 标志可帮助编排器识别嘈杂的评估，而不会强制获得不良分数
- 对于单例评估，协调器提供集群摘要（不是完整内容）以保持判断上下文精简
- 每个子代理独立评估一批——子代理看不到彼此的结果
- **这种独立性是必需的，而不仅仅是首选。** 这些分数决定接受或恢复，因此法官必须与提出假设和运行实验的人处于不同的环境中。如果无法调度，则阻止裁判传球，而不是在内线得分。协调者对自己的实验进行评分并不是一种衡量标准。
