# ce-compound-refresh：看懂旧流程里的刷新命令

如果旧计划写着“升级编码器后运行 `ce-compound-refresh`”，不用再找一个知识库。这是固定上游版本保留的旧名字，实际刷新由 [ce-compound](ce-compound.md) 完成。

`/skill:ce-compound-refresh 仅复核 docs/solutions 里与 UTF-8 长度有关的条目，指出当前哪些测试仍能支持它们。`

输入是已有条目和变更后的实现。刷新可能更新过期说明；想先审查时应明确要求只列差异。新版工作流直接写 `/skill:ce-compound mode:refresh`，不要两个入口各跑一次。只有“文件久没改”而没有相反证据，不足以删除经验。
