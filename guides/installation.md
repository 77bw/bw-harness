# 安装与卸载

安装需要 Git、Node ≥22.19 与 npm、Pi、Python 及 uv。进入本包根目录，执行 `npm ci --ignore-scripts --legacy-peer-deps`；该步骤下载锁定的运行依赖。然后执行 `pi install <本包绝对路径>`，用 `pi list` 核对来源，重开 Pi 查看 `/skill:bw-help`。不要同时注册 Matt/CE 原包；若已装，先识别同名来源，经授权决定保留哪份，不自动卸载。`pi remove <同一绝对路径>` 只解除注册，不删除项目。

Claude Code 可用 `claude --plugin-dir <本包绝对路径>` 启动单次试用，无须改全局。Codex 使用 `codex plugin marketplace add <本包绝对路径>`，再 `codex plugin add bw-harness@bw-harness`；`codex plugin list` 核对 installed, enabled。卸载前核对该宿主的 plugin remove 帮助及源名称。Codex 0.153.4 在临时 CODEX_HOME 成功安装，`$bw-help` 实际读取插件内 Skill 和项目的 GLOSSARY/status；其他入口不因此视作通过。Claude Code 2.1.322 的 manifest 校验通过，但模型网关 ECONNRESET，未能验收调用。Windows 未实测。

Git 安装：`pi install git:github.com/77bw/bw-harness@v1.0.0`；源码安装先 `git clone -b v1.0.0 https://github.com/77bw/bw-harness.git`，再按首段注册。包升级不会更新业务文件；业务模板升级应在可回退 Git 基线上比较 answers 中修订，再审查 Copier 冲突。未验证升级时不要在唯一工作副本运行。

BW 只提供已注册的本地工程路线。上游提到的远程 PR、发布、营销、产品战略和自动交付不属于本包；不要推荐、安装或代跑未注册的 Skill。导航用 bw-help，遇到未启用的路线，说明边界并返回调用方。
