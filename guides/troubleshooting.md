# 排错

未发现 Skill：先比对 `pi list` 的路径、npm 锁和 `node_modules/pi-subagents/index.js`；本地注册不会执行 npm ci。必要时重开会话，不要卸载其他插件来掩盖问题。

`No API key found` 表示模型调用不可用，不代表 Skill 未发现。用 `pi auth check --provider <provider> --model <model>` 区分认证与加载；不要把密钥写进仓库。

`nonempty target` 是保护，不是覆盖提示。改跑 check 并审查迁移批次。路径含空格须整体引用；Git 模板无 HEAD 时只能在测试夹具或有修订的克隆生成。结构检查失败按报告的路径判断违规，不应删除唯一数据来求绿。
