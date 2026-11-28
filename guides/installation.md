# 安装、升级与卸载

安装给宿主注册 Skill；接入才会按项目实际情况合并文档。两步分别验证。业务项目不需要安装 Copier、uv 或一套固定测试工具。Pi 路线需要可用的模型、Git、npm 及兼容的 Node（本包依赖要求至少 22.19）。

## Pi：注册一种来源

已发布版本按 Git 标签安装。在安装前先运行 `git ls-remote --tags https://github.com/77bw/bw-harness.git refs/tags/v1.1.0`；只有返回该标签才使用以下命令：

```sh
pi install git:github.com/77bw/bw-harness@v1.1.0
pi list
```

测试未发布候选版时，检出要测的修订，在**包目录**执行：

```sh
npm ci --ignore-scripts --legacy-peer-deps
pi install "$PWD"
pi list
```

进入**另一个业务目录**新开 Pi，以 `/skill:bw-help 仅说明接入前先检查什么` 验证调用；核对加载位置与安装源一致。有注册记录不等于模型、工具或子 Agent 能工作。Git 安装与本地注册择一；重名时识别来源，不删除个人全局 Skill。

## 其他宿主

- Claude Code：`claude --plugin-dir /path/to/bw-harness`；在该会话使用 `/bw-harness:bw-help`。包路径换成当前检出的绝对路径。
- Codex：从包目录运行 `codex plugin marketplace add "$PWD"`、`codex plugin add bw-harness@bw-harness` 后，新会话使用 `$bw-help`。用 `codex plugin list` 核对来源及启用状态。
- 本手册中的 `/skill:…` 是 **Pi 对话输入**，不是 shell 命令或通用宿主语法。发现、模型实际调用、子任务派发、跨会话恢复是不同能力；兼容性以对应修订的实际验收为准。操作系统上的包检查不证明该系统已跑模型。

### 简体中文版的验证范围

本文面向 v1.1 简体中文候选版。优先按上面的本地方式注册，不使用已撤回的旧标签或缓存。正文、提示词、引用说明和业务模板使用简体中文；Skill 名、命令、路径、字段、枚举及必须精确匹配的契约标题保留原样。旧英文修订的端到端记录不算中文版本通过。发布和宿主支持以对应简体中文修订的实测为准。

## 升级

先升级注册源，再到业务项目运行 `/skill:setup-bw-harness update`。新版不生成 Python 工程；只更新可识别的 BW 规则，保留项目原有约定，实质冲突先核对。旧资料归位用治理的 migrate，不对业务代码做模板升级。Pi 解除注册使用 `pi remove` 加上 `pi list` 中的实际源，不删除业务仓文件。
