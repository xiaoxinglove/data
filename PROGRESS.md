# 项目进度

更新日期：2026-09-20

## 当前交付：F001 最小可运行 MVP

已实现可复现依赖、本地 OAuth 2.0 客户端凭据、受保护 API、本地文档写入与
关键词检索、OpenAI 兼容模型调用、验证器和真实 HTTP 端到端测试。

## 分层验证

| 层级 | 命令 | 结果 |
| --- | --- | --- |
| 依赖锁定 | uv sync --locked | 通过，29 个包 |
| 静态检查 | uv run ruff check . | 通过 |
| 类型检查 | uv run mypy | 通过，20 个源文件 |
| 单元 | uv run pytest tests/unit -q | 4 passed |
| 集成 | uv run pytest tests/integration -q | 5 passed |
| 端到端 | uv run python scripts/http_check.py | 通过，Uvicorn 与本地假模型 |
| 完整入口 | uv run python scripts/check.py | 通过，生成 .check_data/F001.json |

严格按单元、集成、端到端顺序执行。测试客户端产生两条上游弃用警告，
不影响结果。端到端不读取 .env，不调用真实模型。

## 验证器自测

单元测试模拟集成层失败，确认端到端层不执行。结果文件只在全部成功后写入。

## README 同步记录

- 触发变化：依赖、OAuth 配置、资源接口、令牌端点、存储、模型调用和命令。
- 对应段落：README 的接口、环境、运行、数据限制和验证范围。
- 核对依据：pyproject.toml、uv.lock、app/main.py、app/security/oauth.py、
  app/store.py、app/llm.py、run.ps1 和 scripts/check.py。
- 结果：当前行为、配置、命令与限制已同步；F002 未写成已实现。

## 当前限制

- 关键词匹配不是向量 RAG；无租户、用户或来源权限隔离。
- 本地 JSON 不支持多进程写入。
- 本地 OAuth 签发仅适合 MVP；生产需要独立身份提供方和 TLS。
- 渠道、Agent、Memory、MCP、Evaluation 与 RBAC 仍是未启用占位。
- 模型接口没有重试、流式输出、限流或内容审计。

## 自动结果与功能状态

F001 状态由 scripts/check.py 写入 .check_data/F001.json；功能清单只指向结果。
F002 未激活。

## 下一步

F001 交付完成后等待下一项产品决策。若继续建设知识问答，先评审并激活 F002。
