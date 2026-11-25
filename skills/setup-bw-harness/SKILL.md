---
name: setup-bw-harness
description: 在新项目初始化 Python 工程、检查或迁移已有项目时使用。
---

从本 Skill 所在目录定位 scripts/setup.py。先核对目标目录；空目录用 `python3 <脚本> new <目录> --name <包名>`，需要时追加 --api / --research。说明 uvx 下载 Copier 及 uv 安装项目依赖的影响。运行 uv sync、uv run pytest、两项 Ruff 检查和结构检查，再报告。非空目录（含重复 setup）一律先 check，不再生成。migrate 只读交给 project-governance。docs 先列缺失项，获准后才 --apply-docs；已有文件仅提议合并。check 时另核对宿主加载来源、同名冲突、Pi 扩展、工具版本，不安装不修复。
