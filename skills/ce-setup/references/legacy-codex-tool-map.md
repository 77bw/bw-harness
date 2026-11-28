# 删除已退役的Compound Codex工具图

Bun-era `convert` / `install --to codex` 路径将托管块插入到全局 Codex 指令文件中：

`<!-- BEGIN COMPOUND CODEX TOOL MAP -->` … `<!-- END COMPOUND CODEX TOOL MAP -->`

在`${CODEX_HOME:-$HOME/.codex}/AGENTS.md`。该 Claude-compat 映射已过时 - CE 技能名称 Codex 内联工具 - 并且其中一行告诉 Codex 将子代理分派折叠到主线程上。本机插件安装不会添加它，重新运行 Bun CLI for Codex 会删除它。

## 移动

从该文件中删除托管块：行 `<!-- BEGIN COMPOUND CODEX TOOL MAP -->` 到下一行 `<!-- END COMPOUND CODEX TOOL MAP -->`。如果该对不按该顺序作为两整行出现，则该块不存在 - 不进行任何更改。

保持文件的其余部分不变，如果没有留下任何内容，则删除该文件。不要添加替换地图，也不要触及项目或存储库`AGENTS.md`：Bun 安装程序仅写入Codex 主文件。

向用户显示简短的 before/after 更改内容，或者说该块已经不存在。
