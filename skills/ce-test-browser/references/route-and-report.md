# 路由、服务器和报告

在将更改的文件映射到路由之前阅读此内容（工作流程步骤 3）。它携带路由映射起点、端口和服务器命令、每个页面上要检查的内容、两个人性化的提示以及摘要格式。

## 将更改的文件映射到路由

将每个更改的文件映射到呈现它的路由，然后构建要测试的 URL 列表。下表是常见模式的起点，而不是详尽的规则集 - 根据项目的实际布局进行判断：

| 文件模式 | 路线 |
|-------------|----------|
| `app/views/users/*` | `/users`, `/users/:id`, `/users/new` |
| `app/controllers/settings_controller.rb` | `/settings` |
| `app/javascript/controllers/*_controller.js` | 使用该刺激控制器的页面 |
| `app/components/*_component.rb` | 渲染该组件的页面 |
| `app/views/layouts/*` | 所有页面（至少测试主页） |
| `app/assets/stylesheets/*` | 关键页面上的视觉回归 |
| `app/helpers/*_helper.rb` | 使用该帮助程序的页面 |
| `src/app/*` (Next.js) | 对应路线 |
| `src/components/*` | 使用这些组件的页面 |

## 确定端口并验证开发服务器正在运行

`scripts/resolve-port.sh` 解析端口并将其单独打印在标准输出上，因此需要它的 shell 调用会捕获该值，而不是稍后的步骤重新键入打印的数字。如果有显式端口，请附加显式端口作为参数。

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>";
PORT=$(bash "$SKILL_DIR/scripts/resolve-port.sh");
if lsof -i ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Server running on port ${PORT}";
else
  echo "Server not running on port ${PORT}";
  echo "Start your dev server, then re-run:";
  echo "  Rails: bin/dev  or  rails server -p ${PORT}";
  echo "  Node/Next.js: npm run dev";
  echo "  Custom port: run this skill again with --port <your-port>";
  exit 0;
fi
```

## 测试每个受影响的页面

对于每条受影响的路线，使用选定的驱动程序来导航和捕获新的渲染或交互状态。

**验证关键要素：**
- 当前第title/heading页
- 呈现的主要内容
- 没有可见的错误消息
- 表单具有预期字段
- 测试流程没有出现新的控制台错误

**测试关键交互：**从所选驱动程序的最新检查状态派生定位器或元素引用，执行 click/fill/press 操作，然后检查结果状态。不要猜测选择器或重复使用过时的引用。

**截取屏幕截图：**当所选驱动程序支持时，捕获视口和整页证据。当后续工作流程或报告需要文件路径时，将屏幕截图具体化为本地产物；否则应用程序内的证据就足够了。

## 人工验证（需要时）

| 流量类型 | 问什么 |
|-----------|-------------|
| 开放认证 | “请使用 [provider] 登录并确认其有效” |
| 电子邮件 | “检查您的收件箱中是否有测试电子邮件并确认收到” |
| 付款方式 | “在沙盒模式下完成测试购买” |
| 短信 | “验证您收到短信代码” |
| 外部API | “确认[服务]集成正在运行” |

使用平台的提问工具询问用户（列表在SKILL.md步骤6），或呈现编号选项并等待：

```
Human Verification Needed

这个测试涉及到【流量类型】。请：
1. [采取的行动]
2. [要验证什么]

它工作正常吗？
1. 是 - 继续测试
2. 否 - 描述问题
```

## 处理失败

1. **记录失败：**
   - 捕获所选驱动程序的错误状态的屏幕截图
   - 注意准确的复制步骤

2. **询问用户如何继续：**

   ```
   测试失败：[路线]

   问题：[描述]
   控制台错误：[如果有]

   How to proceed?
   1. 立即修复 - 调试并修复失败的测试
   2. 跳过 - 继续测试其他页面
   ```

3. **如果“立即修复”：** 调查、提出修复方案、应用、重新运行失败的测试
4. **如果“跳过”：**记录为已跳过，则继续

## 测试总结

```markdown
## 浏览器测试结果

**测试范围：** PR #[编号] / [分支名称]
**服务器：** http://localhost:<port>

### 测试页数：[计数]

| 路线 | 地位 | 笔记 |
|-------|--------|-------|
| `/users` | 经过 | |
| `/settings` | 经过 | |
| `/dashboard` | 失败 | 控制台错误：[消息] |
| `/checkout` | 跳过 | 需要付款凭据 |

### 控制台错误：[计数]
- [列出发现的所有错误]

### 人工验证：[计数]
- OAuth 流程：已确认
- 电子邮件发送：已确认

### 失败：[计数]
- `/dashboard` - [问题描述]

### 结果：[PASS / FAIL / 部分]
```
