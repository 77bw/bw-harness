# `agent-browser` 后备驱动程序

仅在主要技能选择`agent-browser`后才阅读此文件，因为没有合格的主机原生集成浏览器可用。

## 引导程序

验证直接CLI是否已安装：

```bash
command -v agent-browser >/dev/null 2>&1 && echo "Ready" || echo "NOT INSTALLED"
```

如果丢失，则告诉用户：“`agent-browser`未安装。使用`ce-setup`技能打印当前安装命令，然后安装`agent-browser`并重试。”然后停下来。安装的发现技能并不意味着已安装 CLI 或其浏览器运行时。

在运行浏览器操作之前，加载与已安装的 CLI 匹配的工作流程和故障排除内容：

```bash
agent-browser skills get core
```

如果 CLI 存在但无法启动其浏览器，请按照当前的核心故障排除说明进行操作并报告确切的启动失败情况。不要将缺少的浏览器运行时或启动错误错误报告为缺少 CLI。

## 该技能使用的命令

当手动模式选择可见浏览器时，将 `--headed` 添加到命令中。管道模式默认将此后备驱动程序设置为无头驱动程序。

```bash
# Navigate and inspect
agent-browser open <url>
agent-browser snapshot -i

# Interact using refs from the latest snapshot
agent-browser click @e1
agent-browser fill @e1 "text"
agent-browser type @e1 "text"
agent-browser press Enter

# Capture evidence
agent-browser screenshot out.png
agent-browser screenshot --full out-full.png

# Navigation and waits
agent-browser back
agent-browser wait @e1
```

使用已安装的核心文档进行控制台错误检查以及此处未显示的任何命令。第一个路由测试完毕后，请勿切换到其他浏览器驱动程序。
