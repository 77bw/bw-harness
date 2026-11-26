# BW Harness

BW Harness 是给 **用 AI 开发 Python 项目的人**准备的工具包。它不是另一个 Agent：你继续在 Pi 里工作，Harness 提供项目模板和一组可点名调用的工作方法（Skill）。

比如你要写一个消息编码器：先生成能导入、能跑测试的 Python 包，再和 Agent 定下“长度按字节还是字符算”，把决定交给实施计划。做到一半换会话，新会话可以从项目里的术语表、计划和状态文件继续，不用从聊天记录重新猜。小修复不用走整套流程。

## 快速开始：生成你的第一个项目

需要已能调用模型的 Pi、Git、Node.js ≥22.19、npm、Python 和 uv。无需单独安装 Matt Pocock 或 Compound Engineering。以下示例使用 macOS 终端。

**1. 在终端安装一次**，然后从你平时放项目的目录创建一个新目录。不要在本仓库里初始化业务代码。

```bash
pi install git:github.com/77bw/bw-harness@v1.0.0
mkdir frame-demo
cd frame-demo
pi
```

**2. 在 Pi 对话里输入**（不是终端命令）：

```text
/skill:setup-bw-harness new 在当前空目录创建 Python 包 frame_demo，不启用 API。安装依赖并运行检查，不提交 Git。
```

**3. 在 `frame-demo` 目录的终端验证：**

```bash
uv run python -c "import frame_demo; print(frame_demo.__name__)"
uv run pytest -q
```

第一条应打印 `frame_demo`，第二条应有测试通过。此时 `src/frame_demo/` 是你要开发的包，`tests/` 是它的测试；`.copier-answers.yml` 记录模板来源。接下来可以在 Pi 里问 `/skill:bw-help 我想为这个包增加一个编码函数，从哪里开始？`

## 已经有项目？不要用 `new`

在**已有项目的根目录**启动 Pi，输入 `/skill:setup-bw-harness check 只读检查，不移动文件、不安装依赖`。先看它指出哪些文件缺失、哪些目录需要解释，再决定要不要改。[已有项目迁移示例](guides/workflows/existing-project.md)

## 接下来读什么

- [快速上手](guides/quick-start.md)：从空目录到第一次测试，再把一个具体任务交给 Agent。
- [使用手册](guides/README.md)：按“修 Bug、迭代算法、换会话”等场景找路线，或查全部 28 个 Skill。
- [安装与兼容性](guides/installation.md)：Pi 是首选；Codex 实测过导航调用，Claude Code 的模型调用未验收，Windows 未实测。

自研内容采用 [MIT](LICENSE)。本包是独立发行，不是 Matt Pocock 或 Every 官方插件；内置版本与资源见[上游锁](upstream.lock.yml)，原版权声明见[许可证目录](licenses/)。
