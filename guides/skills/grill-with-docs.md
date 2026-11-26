# grill-with-docs：边问边记下影响实现的决定

“长度最大 255”听起来明确，遇到中文才发现两人说的不是同一个长度。还没写代码时就值得把这个分歧问清。

```text
/skill:grill-with-docs 我要做一字节长度前缀的文本帧。请用空串和「你」帮我确认载荷、长度单位和超长输入的行为，一次问一个会改变实现的问题。
```

你负责选择业务语义，Agent 用反例追问，并借助 [grilling](grilling.md) 和 [domain-modeling](domain-modeling.md) 更新确认过的术语。难逆转的取舍才写 `docs/adr/`。检查 `GLOSSARY.md` 讲的是这个词在项目里是什么意思，而不是把整场谈话抄进去。

决定充分后，把目标、非目标、边界和验收条件交给 [ce-plan](ce-plan.md)。已有明确决策就直接传过去，不要为了产出文档再访谈一轮。

执行依据：[grill-with-docs 正文](../../skills/grill-with-docs/SKILL.md) · Matt `6f7f783`（[修订与适配](../../upstream.lock.yml)）；其他宿主的调用方式见[安装指南](../installation.md)。
