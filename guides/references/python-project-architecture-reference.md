# Python 项目架构参考（可选）

> 用途：作为 BW Harness 之外的独立架构参考，适用于 Python 数据采集、合法协议研究、算法开发和可选 Web API。不是强制项目规范，不属于默认 Skill 工作流。已有项目可保持原结构；只有用户明确要求架构设计或重构时才参考本文件。
>
> 参考来源：[vibe-coding-cn 通用项目架构模板](https://github.com/2025Emma/vibe-coding-cn/blob/main/i18n/zh/documents/Templates%20and%20Resources/%E9%80%9A%E7%94%A8%E9%A1%B9%E7%9B%AE%E6%9E%B6%E6%9E%84%E6%A8%A1%E6%9D%BF.md) 中 Python Web/API、数据科学项目的职责分离思想，以及此前 BW Harness 的 A/B/C 方案。本文件为结合研究型 Python 项目整理的建议，不是原模板的逐字复制。

## 1. 使用原则

- 保持现有项目业务入口和可运行行为；不要仅为了符合目录树而重构。
- 新项目按实际需求创建模块，先平铺，再拆分。无需预建空目录。
- 推荐 src 布局、uv、pytest、Ruff，但不排斥已有依赖管理、测试工具、包组织或其他语言。
- 以下目录均为可选示例；仅在需要时添加网络、算法、持久化、Web API 等能力。

## 2. 轻量项目（方案 A）

```text
project/
├── src/project_name/
│   ├── __init__.py
│   ├── __main__.py         # CLI，可选
│   ├── config.py
│   ├── client.py           # 请求外部接口
│   ├── protocol.py         # 协议数据结构与编解码
│   ├── algorithms.py       # 独立算法
│   ├── parser.py           # 结果解析
│   ├── service.py          # 业务编排
│   └── models.py
├── tests/
│   ├── test_algorithms.py
│   └── fixtures/
├── scripts/                # 可长期复用的辅助工具
├── experiments/            # 可复现实验，可选
├── docs/                   # 使用项目现有文档约定
├── .local/                 # 临时脚本、原始证据、日志；不提交
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
└── .gitignore
```

以上并不是最小生成清单；单一功能可能只需要一个业务模块和对应测试。已经使用平铺结构的项目不必强制迁到 src。

## 3. 标准研究型项目（方案 B）

```text
project/
├── src/project_name/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── core/               # 日志、公共基础能力
│   ├── transport/          # HTTP/连接/重试等传输能力
│   ├── clients/            # 外部接口客户端
│   ├── protocols/          # 消息格式、序列化、编解码
│   ├── algorithms/         # 正式算法
│   │   ├── encoding.py
│   │   ├── decoding.py
│   │   └── checksum.py
│   ├── parsers/            # 业务响应解析
│   ├── models/             # 数据模型
│   ├── services/           # 业务流程
│   ├── storage/            # 文件、缓存、数据库适配，可选
│   └── api/                # 对外 Web API，可选
│       ├── app.py
│       ├── dependencies.py
│       ├── schemas.py
│       └── v1/routes.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── fixtures/
│       ├── vectors/        # 脱敏、确定输入输出
│       └── responses/
├── experiments/
│   ├── algorithms/
│   ├── protocols/
│   └── benchmarks/
├── scripts/
├── configs/                # 非敏感配置，可选
├── docs/                   # 项目采用的实际文档体系
├── .local/
│   ├── scratch/
│   ├── captures/
│   ├── artifacts/
│   ├── reports/
│   ├── data/
│   └── logs/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
└── .gitignore
```

省略了部分子包的 `__init__.py`；实际使用时按 Python 打包方式补充。目录职责如下：

| 模块 | 建议职责 |
|---|---|
| transport | 网络传输、连接、超时与重试，不负责业务解析 |
| clients | 外部服务契约及接口调用 |
| protocols | 消息结构与格式转换 |
| algorithms | 尽量纯粹、可单独验证的计算逻辑 |
| parsers | 业务响应解析 |
| models | 内部数据结构 |
| services | 编排业务操作，复用底层模块 |
| api | 对外路由、参数校验与响应格式，不复制业务实现 |
| storage | 持久化及缓存适配 |
| core | 真正可共享的基础能力，不作杂物目录 |

推荐依赖方向：SDK/CLI/Web API → services → clients/protocols/algorithms/parsers；clients → transport。算法不应反向依赖 Web API 或业务流程。具体关系以项目实际需要为准。

## 4. 多平台项目（方案 C）

当多个平台确实需要独立实现时，可按平台就近组织代码，不提前建立空抽象：

```text
src/project_name/
├── core/
├── transport/
├── algorithms/             # 真正可共享的算法
├── models/
├── platforms/
│   ├── platform_a/
│   │   ├── client.py
│   │   ├── protocol.py
│   │   ├── algorithms/
│   │   └── parser.py
│   └── platform_b/
│       ├── client.py
│       ├── protocol.py
│       ├── algorithms/
│       └── parser.py
├── services/
└── api/
```

平台共享代码在存在实际复用需求时再提取。不要仅因未来可能有平台 B 而提前拆分平台 A。

## 5. 算法版本与实验管理建议

| 资产 | 建议位置 |
|---|---|
| 一次性实验 | `.local/scratch/` |
| 需要长期复现的实验 | `experiments/` |
| 正式算法 | `src/.../algorithms/` 或已有等价位置 |
| 确定性测试向量 | `tests/fixtures/vectors/` |
| 原始研究证据 | `.local/` 或经批准的受控备份 |
| 研究结论 | 项目的研究文档，如 `docs/research/` |

算法修改历史由 Git 保存；普通 Bug 修复、性能优化原地修改。只有真实兼容需求才保留 `v1.py`、`v2.py` 等运行版本，分别测试适用范围。不要因为修改次数创建 `final`、`new`、`fix` 副本。JS/Go 等参考实现可按语言放入实验目录；如果生产运行确需依赖，则放在正式模块中并记录构建依赖。多个实现尽量共享独立测试向量，避免用候选算法自身生成的预期输出作为唯一验证。

正式算法晋升：明确输入/输出 → 独立向量及边界测试 → 候选对比 → 正式实现回归 → 更新相关研究结论。原始敏感数据不提交，重要唯一证据不能因目录整理丢失。

## 6. Web API（可选）

当确实需要对外提供服务时再引入 FastAPI 等框架。API、CLI 和 SDK 复用同一业务层；业务代码不直接依赖路由。数据库、队列、Docker、任务调度等随需求引入，不是模板默认依赖。Web API 的版本与算法兼容版本独立。

## 7. 给 AI 的参考用法

只有需要代码架构建议时，将本文件作为输入，例如：

> 参考 python-project-architecture-reference.md，根据当前项目的真实规模、现有代码和功能需求提出最小的目录组织建议。优先保持原有运行行为，不机械套用模板，不自动创建空目录或重构现有项目。

本文件不定义 BW Harness 的文档治理、Git 交付策略或任务执行流程；这些由项目当前规则与原生 CE 工作流负责。
