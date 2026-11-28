# Python 项目结构：从一个包开始

这些路径相对于**生成的业务项目**，不是 BW Harness 仓库。假设包名是 `frame_demo`，第一次打开时先认四个位置：

```text
src/frame_demo/              Python 实际导入的代码
tests/                       已安装包的行为和回归测试
scripts/check_structure.py   检查目录归属、违规引用和误跟踪文件
docs/status.md               下一次工作从哪接着做
```

**轻量项目不需要先建十个目录。** 第一个编码函数可以直接放在 `src/frame_demo/codec.py`，测试从 `frame_demo.codec` 导入它。实现多了，才把消息格式拆到 `protocols/`、纯计算拆到 `algorithms/`。若从单文件改成包，替换旧入口，不同时维护两份实现。

## 一段试验代码怎么变成正式代码？

以比较字符数和 UTF-8 字节数为例：先在 `.local/scratch/` 验想法；如果同事需要重跑，将运行入口和目的放到 `experiments/`。预期值保存在 `tests/fixtures/vectors/`，标注来源，别让实验和测试各维护一份。通过边界用例后，把稳定实现放回 `src/`。**正式包不能导入 `experiments` 或 `tests`**，否则用户安装后可能缺文件。[看完整示例](workflows/algorithm-development.md)

## 什么时候值得加一层？

- 有网络连接和重试才需要 `transport/`；具体服务的请求契约归 `clients/`。编码函数只收数据，不负责联网。
- 当 CLI 和可选的 FastAPI 都要执行同一业务动作，把它放在 `services/`，入口只做参数转换。没有 Web 需求就不要选 API 模板。
- 确有不同平台的协议和实现时，才按 `platforms/<平台>/` 分开；普通修订交给 Git，不复制 `codec_final_v2.py`。

改完在项目根目录执行 `uv run python scripts/check_structure.py` 和 `uv run pytest -q`。前者能指出特定路径或导入违规，不能证明模块划分合理；后者才验证已有测试覆盖的行为。
