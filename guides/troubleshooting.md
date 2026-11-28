# 排错：先分清是哪一步没成功

**`pi list` 没有 BW Harness，或对话里没有 `/skill:bw-help`。** 在终端运行 `pi list`。没有记录就回到[安装](installation.md)；有记录则确认源是期望的标签或克隆目录，再到业务目录新开 Pi。本地注册不会安装依赖，回到包目录检查 `node_modules/pi-subagents/index.js` 是否存在；缺失时按本地安装步骤运行 `npm ci`。不要在业务项目里重装 npm 包碰运气。

**同一个名字出现两次。** 比较来源：是否同时注册了 Git 和本地路径，或已有独立 Matt/CE？先决定保留哪份，再用对应源名解除多余的注册。不要删除其他包中的文件，也不要为了测试覆盖全局配置。

**命令能找到，但模型不回答。** `No API key found` 是模型认证问题，不是 Skill 缺失。用 `pi auth check --provider <provider> --model <model>` 检查所选模型（替换尖括号内容）；不要把凭据贴到 README 或错误报告。Claude 的 `ECONNRESET` 表示连接被重置，不能推断清单加载失败。

**`new` 报 `nonempty target`。** 查看当前目录是否已有源码、文档或隐藏文件。这是防覆盖保护：要开新项目就另建空目录；要保留内容就在原目录请求 `/skill:setup-bw-harness check 只读检查`。不要先删文件。

**结构检查返回非零。** 在项目根重跑 `uv run python scripts/check_structure.py`，从报告的第一条路径查起。如果是 `.local/`，用 `git ls-files -- .local` 分辨“被 Git 跟踪”和“仅在本地存在”；先保护唯一证据，不要为消掉报错而删数据。若 `pytest` 显示没有测试，也不算通过。

**路径或升级失败。** 含空格的路径整体加引号；核对 `.copier-answers.yml` 指向的模板源和修订是否仍可访问。升级冲突先在可回退的副本处理，保留差异，再决定是否采用。报告问题时提供宿主版本、操作目录类型、第一条失败命令和脱敏报错，不附会话记录。
