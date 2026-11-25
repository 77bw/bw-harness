# 从轻量包演进到多平台

A：默认只有 src 包、测试和维护脚本。B：有协议后才拆 protocols，有独立纯函数才拆 algorithms，由 services 编排；clients 依赖 transport，不让底层依赖 API。C：确有互不兼容的平台才建 platforms/<平台>，公共能力只提取一次。FastAPI 是可选入口，不复制服务逻辑。

一次性数据放 .local；值得重跑的候选进 experiments；已验证实现进 src，向量放 tests/fixtures/vectors。格式版本与实现修订不同，后者用 Git，不创建 final_v2 副本。
