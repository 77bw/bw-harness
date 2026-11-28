# 快速上手：让 Pi 在空目录里生成一个能测试的包

目标是运行**你的新项目**，不是测试 BW Harness 仓库。以下命令假设你在 macOS 终端，Pi 已登录，且已按[安装指南](installation.md)装好 v1.0.0。若目录里已经有代码，改看[已有项目](workflows/existing-project.md)。

### 1. 选对工作目录

在平时放项目的目录执行；若 `frame-demo` 已存在，换一个新名字，不要清空旧目录。

```bash
mkdir frame-demo
cd frame-demo
pi
```

### 2. 让 Pi 初始化，不自己复制模板

在 **Pi 对话**输入：

```text
/skill:setup-bw-harness new 在这里创建 frame_demo。用轻量模板，不加研究目录和 FastAPI；可以安装依赖、运行测试，不做 Git 提交。
```

`frame-demo` 是磁盘目录，`frame_demo` 是 Python 导入名。首次运行会下载 Copier 和项目依赖。完成后看 `src/frame_demo/__init__.py`、`tests/test_import.py` 和 `.copier-answers.yml`；三个文件分别告诉你“代码放哪”“怎样证明能导入”“用的哪一版模板”。

### 3. 验证的不只是“文件建好了”

另开终端，进入刚才的 `frame-demo` 目录，执行：

```bash
uv run python -c "import frame_demo; print(frame_demo.__name__)"
uv run pytest -q
uv run python scripts/check_structure.py
```

应看到包名 `frame_demo` 和通过的导入测试；结构检查正常时可以没有输出，退出码应为 0。这只证明项目能运行，还没有实现任何编码算法。失败时保留第一条出错命令和报错，去[排错](troubleshooting.md)，不要再跑一遍 `new`。

### 4. 把第一个任务说具体

回到 Pi：`/skill:bw-help 我想支持空串和中文消息。还没决定长度字段按什么单位算，请只推荐下一步。` 正常结果是一个建议，不是自动改代码。想继续开发时，沿[新项目工作流](workflows/new-project.md)把决定交给计划和测试。
