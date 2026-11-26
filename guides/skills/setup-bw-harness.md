# setup-bw-harness：让目录具备可验证的开发起点

在终端里 `cd` 到目标目录再启动 Pi。安装包装的是工具；这个入口决定工具能对**当前项目**做什么。不要站在 Harness 源码目录里让它“新建项目”。

| 目录状况 | Pi 输入示例 | 会改变什么 |
|---|---|---|
| 新建空目录 | `/skill:setup-bw-harness new 创建 frame_demo，不开 API，安装依赖并运行 smoke test。` | 调用 Copier 生成 `src/frame_demo/`、测试、文档和 answers。 |
| 已有工程，先了解情况 | `/skill:setup-bw-harness check 只读报告缺项和重名来源。` | 不写文件、不安装；缺项是诊断，不是覆盖许可。 |
| 只想补文档 | `/skill:setup-bw-harness docs 列出缺失文件，先不要写。` | 先预览，批准后只新增缺项；已有规则另行比较。 |
| 要搬旧文件 | `/skill:setup-bw-harness migrate 列迁移清单和回退方法。` | 先诊断并交给治理；没批准具体批次不移动。 |

新项目看两项结果：`.copier-answers.yml` 有来源和修订，`uv run pytest -q` 真正运行了至少一个测试。再次运行 `new` 被拒绝是保护；复查用 `check`。下一步看[第一个功能](../workflows/new-project.md)。
