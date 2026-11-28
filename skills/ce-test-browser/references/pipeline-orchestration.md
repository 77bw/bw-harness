# 管道模式服务器编排

仅当使用 `mode:pipeline`（LFG 或其他自动运行器）调用时才读取并遵循此文件。它会覆盖可见性提示、自由端口选择和开发服务器启动。它不会更改浏览器驱动程序选择。在管道模式下，您可以在无人值守的情况下运行——永远不会阻塞问题。

运行报告（无论是摘要还是停止测试的预检阻塞项）是该技能写入的最后内容。它结束了该技能，而不是回合。调用者在同一个会话中运行，其下一步遵循报告。

## 1. 没有可见性问题

无人值守执行并不意味着隐藏执行。不要问可见性问题：

- 当选择主机本机集成浏览器时，保持其正常集成表面可见且无阻塞，以便用户可以在不中断运行的情况下观看进度。不要重复窃取焦点。
- 当选择后备`agent-browser`驱动程序时，无头运行它而不通过`--headed`。

## 2. 申请一个空闲端口并启动服务器

多个代理可能在同一台机器上运行，因此永远不要假设解析的端口是空闲的：此技能目录中的`scripts/resolve-port.sh --free`解析端口并向上扫描到没有侦听器的第一个端口，将其单独打印在标准输出上。

作为**一个**命令运行整个过程。 Shell 变量在单独的 Bash 调用之间无法生存，因此端口解析、自由扫描和启动都发生在该块内 - 它通过捕获脚本的输出而不是从之前打印的任何内容来播种 `PORT`。当用户给出 `--port N` 或您的上下文项目指令声明开发服务器端口时，添加显式端口作为第二个参数。

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PORT=$(bash "$SKILL_DIR/scripts/resolve-port.sh" --free);   # append the explicit port as a further argument when you have one
echo "Using dev server port: $PORT"

# start in the background (the scan guarantees this port is free), then wait up to 30s
echo "Starting dev server on port ${PORT}..."
if [ -f "bin/dev" ]; then
  PORT=${PORT} bin/dev > /tmp/dev-server-${PORT}.log 2>&1 &
elif [ -f "bin/rails" ]; then
  bin/rails server -p ${PORT} > /tmp/dev-server-${PORT}.log 2>&1 &
elif [ -f "package.json" ]; then
  PORT=${PORT} npm run dev > /tmp/dev-server-${PORT}.log 2>&1 &
fi
for i in $(seq 1 30); do
  lsof -i ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1 && break
  sleep 1
done
if ! lsof -i ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Server did not start in 30s. Last output:"
  tail -20 /tmp/dev-server-${PORT}.log 2>/dev/null
  exit 1
fi
```

扫描可能会落在与已解析端口不同的端口上，并且 `$PORT` 不会保留到以后的 shell 调用中。请注意此块回显的数字（“使用开发服务器端口：N”）并在每个后续选定驱动程序导航中使用该文字端口 - 不要依赖 `${PORT}` 继承。然后返回到“测试每个受影响的页面”步骤，导航到`http://localhost:<N>`，检查渲染状态并测试每个路由。
