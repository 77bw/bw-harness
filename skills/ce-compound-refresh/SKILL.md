---
name: ce-compound-refresh
description: "令人耳目一新的学习的旧名称，现在位于`ce-compound`。仅当提示或常设指令名称为 `ce-compound-refresh` 时使用；使用 `ce-compound` 进行其他所有学习审核。"
argument-hint: "[可选：范围提示 — 目录、文件名、模块或关键字] [mode:non-interactive]"
---

> 本包以简体中文撰写说明、选项及面向用户的输出。Skill 名称、命令、路径、字段、枚举、原文引述及要求精确匹配的契约标记保持原样。

# 复合刷新（已弃用）

该名称仍然有效，因此现有的提示和计划将继续运行。刷新本身现在位于`ce-compound`。

**完成：** 通知在刷新之前和之后显示，并且刷新按照要求的范围和模式运行。

在活动主机的通知中呈现调用：默认为 `/skill-name`，在 Codex 或记录美元前缀调用的其他主机上渲染 `$skill-name`。只输出一种形式。

按顺序执行这些操作：

1. 打印此通知，除渲染外未做任何更改：

   > ⚠️ `/ce-compound-refresh` 已合并到 `/ce-compound` 并将在即将发布的版本中消失。此运行正常进行。下次使用`/ce-compound refresh`。

   如果您的参数包含 `mode:non-interactive` 或 `mode:headless`，请以此结束通知，因为没有人在场，并且普通单词将运行捕获：下次，使用 `/ce-compound mode:refresh mode:non-interactive`。

2. 使用 `mode:refresh` 调用 `ce-compound` 技能，后跟您收到的每个参数，保持不变。 `mode:refresh` 必须存在：没有它，无人值守运行将执行捕获而不是刷新。
3. 完成后，再次打印通知作为最后一行。刷新报告很长，并且计划的运行可能仅显示其最终消息。
