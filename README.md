# BW Harness

BW Harness 帮助开发者在多个 AI 会话之间继续同一项工作：用 Matt 的访谈厘清领域语言，用 Compound Engineering（CE）规划、实施、验证、审查和交付，用项目自己的文档保存决定、证据与下一步。**接入改变工作约定，不替你选语言、创建代码目录或安装项目技术栈。**

## 从已有项目开始

在已配置模型的 Pi 安装本包（[安装方式与版本说明](guides/installation.md)），进入业务项目目录，在 Pi 对话中输入：

```text
/skill:setup-bw-harness check 请先检查现有指令、文档根、Git 和实际验证入口，不写文件。
/skill:setup-bw-harness 接入当前项目，保留现有规则和代码。只对实际冲突向我确认。
/skill:bw-help 我已有一个实施计划，接下来从哪继续？
```

第一次接入空目录也用同一个 setup。它读随 Skill 分发的模板，合并项目指令、工作流和真实状态；没有术语、重大决策或经验时不创建空文档。`check` 不写文件，升级工作约定用 `update`。普通开发无需反复初始化。

- [快速上手](guides/quick-start.md) · [现有项目与旧知识迁移](guides/workflows/existing-project.md)
- [文档分别负责什么](guides/document-structure.md) · [暂停与跨会话继续](guides/workflows/session-recovery.md)
- [从计划到原生 Git 交付](guides/workflows/git-delivery.md) · [全部 Skill 指南](guides/README.md)

一个包内置所需 Matt、CE 资源与 Pi 扩展，无需另装两套同名 Skill。软件以 Git 标签分发，不是官方 Matt/Every 插件。来源、修订和适配见[上游锁](upstream.lock.yml)、[版权声明](licenses/)和[变更记录](CHANGELOG.md)。
