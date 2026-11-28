# domain-modeling：让两个相似的词不再混用

测试里叫 `message`，接口文档叫“帧”，有人用它们指原始文本，也有人用来指带前缀的字节。先解决名字所指的东西，再讨论实现。

`/skill:domain-modeling 比较“文本消息”“载荷”“帧”的用法；用空串举例。遇到冲突问我，确认后只更新现有 GLOSSARY.md。`

给它当前词表和一两个实际调用位置。结果应是简短定义和能区分近义词的例子；`docs/agents/domain.md` 负责指路，不是第二份词表。若牵涉“为何以后都按字节计数”这样的兼容取舍，可另议 ADR。只是读现有定义时，不需要启动一次建模。

执行依据：[domain-modeling 正文](../../skills/domain-modeling/SKILL.md) · Matt `6f7f783`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
