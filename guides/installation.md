# 安装、升级与卸载

**安装**把 Skill 注册给 Agent，可以供多个项目使用。**初始化**则在某一个项目写 Python 包、测试和规则文件。安装成功后还没有业务项目；反过来，克隆了仓库也不代表 Pi 已经加载它。

## Pi：选一种安装方式

先在终端确认 `pi --version`、`node --version`、`npm --version`、`git --version` 和 `uv --version` 可运行。Node 需要 ≥22.19，模板项目使用 Python ≥3.11。Pi 还需要一个可用的模型；列出 Skill 不代表模型可以回答。

**只想使用：** 在任意目录执行以下命令。Pi 从固定 Git 标签安装包及声明的运行依赖。

```bash
pi install git:github.com/77bw/bw-harness@v1.0.0
pi list
```

**想阅读源码或测试本地改动：** 在放工具的目录执行以下命令（macOS shell）。本地注册不会替你安装 Node 依赖，不能略过 `npm ci`。

```bash
git clone -b v1.0.0 https://github.com/77bw/bw-harness.git
cd bw-harness
npm ci --ignore-scripts --legacy-peer-deps
pi install "$PWD"
pi list
```

两种方式择一。核对 `pi list` 的源是你选择的标签或目录，然后**到业务目录新开 Pi**，输入 `/skill:bw-help 我准备接手旧项目，先做什么？`。看到只读检查的建议，才验证了发现和调用两件事。不要再分别安装 Matt/CE；老环境若出现重名，先[核对来源](troubleshooting.md)。

## Claude Code 和 Codex

先把同一标签的仓库克隆到本地。以下命令在**克隆的包目录**运行，`$PWD` 表示它的绝对路径。若要在另一个项目启动 Claude，把参数换成这个包的实际绝对路径。

| 宿主 | 如何加载 | v1.0.0 验证边界 |
|---|---|---|
| Pi 1.1.0 | 上述 Git 或本地注册 | macOS 上从公共标签发现 28 个 Skill；初始化、测试与会话接续有真实试点。 |
| Claude Code 2.1.322 | `claude --plugin-dir "$PWD"`，单次启动加载 | 清单校验通过；试调用 `/bw-harness:bw-help` 时模型网关返回 `ECONNRESET`，未确认端到端调用。 |
| Codex 0.153.4 | `codex plugin marketplace add "$PWD"`，然后 `codex plugin add bw-harness@bw-harness` | `codex plugin list` 显示 `installed, enabled`；在业务目录用 `$bw-help` 已读到项目术语和状态，不能据此外推所有 Skill。 |

本手册的 `/skill:…` 示例均为 **Pi 对话输入**，不是通用终端命令。Windows 未做端到端验收。

## 升级或移除

更换包版本前先记下 `pi list` 的源。卸载公共标签用 `pi remove git:github.com/77bw/bw-harness@v1.0.0`；本地源则在克隆目录用 `pi remove "$PWD"`。这只解除注册，不会移除你项目里的代码或文档。Claude 单次加载可直接退出；Codex 用 `codex plugin remove --help` 核对已安装的名称再操作。

升级包**不等于**升级已生成的业务项目。后者先看项目的 `.copier-answers.yml`：本地路径要能访问、原修订要能找到。先在可回退的 Git 副本验证 Copier 更新，检查用户修改、ADR 和冲突，再决定是否在原项目应用。不要在非空项目用 `new` 来“升级”。
