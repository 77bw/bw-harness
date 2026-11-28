# 合并并验证忽略规则

检查现有规则和例外，包括以后的覆盖和嵌套文件。仅插入缺失的适用模式，保留用户特定的例外和优先级。常用起始组：

```gitignore
.local/
.context/compound-engineering/
.compound-engineering/*.local.yaml
.env
.env.*
!.env.example
*.log
*.har
*.pcap
*.pcapng
.DS_Store
Thumbs.db
```

已识别的Python/Node项目可能需要忽略其实际缓存、环境或依赖目录；不要将数据或所有灯具列入黑名单。保持所需的编辑示例和跟踪的团队 CE 配置符合版本控制的条件。

使用 `git check-ignore -v --no-index -- <path>` 检查示例路径上的**获胜模式**（包括嵌套的暂存、本地配置、.env、.env.example 和任何保留的固定装置）；获胜的否定是一个例外。使用非详细语法和退出状态验证 positive/negative 结果。使用`git ls-files --cached -- <pathspecs>`查找已跟踪的敏感或本地材料：忽略规则不会取消跟踪。报告路径，而不是内容。既不要默默地取消历史记录，也不要重写历史。保留证据。
