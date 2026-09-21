# 项目进度

更新日期：2026-09-21

## 当前交付：F001 最小可运行 MVP

已实现可复现依赖、本地 OAuth 2.0 客户端凭据、受保护 API、本地文档写入与
关键词检索、OpenAI 兼容模型调用、验证器和真实 HTTP 端到端测试。

## 分层验证

| 层级 | 命令 | 结果 |
| --- | --- | --- |
| 依赖锁定 | uv sync --locked | 通过，29 个包 |
| 静态检查 | uv run ruff check . | 通过 |
| 类型检查 | uv run mypy | 通过，23 个源文件 |
| 单元 | uv run pytest tests/unit -q | 4 passed |
| 集成 | uv run pytest tests/integration -q | 6 passed |
| 安全 | uv run pytest tests/security -q | 11 passed |
| 端到端 | uv run python scripts/http_check.py | 通过，Uvicorn 与本地假模型 |
| 服务实跑 | uv run uvicorn backend.main:app | 通过，401 / 200 / 201 / 502 边界均符合预期 |
| 完整入口 | uv run python scripts/check.py | 通过，生成 .check_data/F001.json |

严格按单元、集成、端到端顺序执行。测试客户端产生两条上游弃用警告，
不影响结果。端到端不读取 .env，不调用真实模型。

## 验证器自测

单元测试模拟集成层失败，确认端到端层不执行。结果文件只在全部成功后写入。

## 文件与代码同步台账

本节是代码、配置、测试和文档同步工作的唯一记录入口。README 保持项目总说明
手册结构并随每次迭代更新，不承担变化日志职责。

| 变更或核对对象 | 受影响说明 | 已同步文件 | 核对依据 | 结果 |
| --- | --- | --- | --- | --- |
| OAuth 2.0、JWT 与 scopes | 安全架构、接口、环境变量、限制 | README.md、DECISIONS.md、docs/api-patterns.md、backend/security/ARCHITECTURE.md、backend/security/PROGRESS.md | backend/security/oauth.py、tests/integration/test_api.py、scripts/http_check.py | 已同步并通过集成、端到端验证 |
| API 路由与请求响应 | 接口概览、调用示例、API 模块状态 | README.md、docs/features.md、backend/api/ARCHITECTURE.md、backend/api/PROGRESS.md | backend/main.py、tests/integration/test_api.py、tests/integration/test_direct_entrypoint.py | 已同步，6 个集成测试通过 |
| 依赖、启动与完整验证 | 环境要求、安装、启动和验证命令 | README.md、Initialization.md、docs/testing-standards.md | pyproject.toml、uv.lock、run.ps1、scripts/check.py | 已同步，完整入口通过 |
| 本地存储、检索与模型 | 当前架构、模块能力和限制 | README.md、backend/rag/PROGRESS.md、docs/features.md | backend/store.py、backend/llm.py、tests/unit/test_mvp.py | 已同步，单元和端到端通过 |
| 企业级 README 重构 | 项目总说明、当前架构、目标架构、模块、部署、安全、路线 | README.md、AGENTS.md、DECISIONS.md、docs/testing-standards.md、PROGRESS.md | 当前代码、配置、测试及 27 份项目文档交叉核对 | 已同步；没有把目标技术写成现状 |
| README 迭代更新规则 | 明确 README 随每次迭代核对更新，PROGRESS 记录同步过程 | README.md、AGENTS.md、DECISIONS.md、PROGRESS.md | 用户要求及现有文档职责交叉核对 | 已同步；消除“稳定手册等于不更新”的歧义 |
| 直接执行 backend/main.py | 入口启动方式、主机与端口配置、回归验证 | README.md、.env.example、backend/api/ARCHITECTURE.md、backend/api/PROGRESS.md、PROGRESS.md | backend/main.py、backend/__init__.py、tests/integration/test_direct_entrypoint.py、用户原始 Conda 命令 | 根因为脚本目录取代项目根目录进入 sys.path，且 Conda 环境存在同名顶层包；修复并增加包冲突回归测试 |
| 应用包 app 重命名为 backend | 全部 import 前缀、mypy 检查范围、启动命令、端到端脚本、测试引用、README 项目结构树 | README.md、PROGRESS.md、AGENTS.md、docs/features.md、docs/api-patterns.md、backend/agent/ARCHITECTURE.md、backend/api/ARCHITECTURE.md、backend/api/PROGRESS.md、backend/evaluation/ARCHITECTURE.md、backend/mcp/ARCHITECTURE.md、backend/memory/ARCHITECTURE.md、backend/rag/ARCHITECTURE.md、backend/rag/PROGRESS.md、backend/security/ARCHITECTURE.md、pyproject.toml、run.ps1、scripts/http_check.py、tests/conftest.py、tests/unit/test_mvp.py、tests/integration/test_api.py、tests/integration/test_direct_entrypoint.py | 全仓库复查 app 引用归零；uv sync --locked、ruff、mypy（23 文件）、单元 4、集成 6、安全 11、HTTP 端到端、scripts/check.py 全通过；另起真实服务校验无令牌 401、带令牌 200、写资料 201、缺模型 Key 502 | 已同步；同时确认 backend/main.py 中 sys.path 原指向 parents[2]/src 属越界且目录不存在，改为 parents[1]；删除并从旧路径搬迁的 .venv 后重建，修复 uv console script trampoline 失效 |

未同步项：`frontend/`、`deploy/` 与 `tests/evaluation/`、`src/` 属于本次任务范围外的新增未跟踪目录，未纳入本次提交。`.vscode/` 是用户本地编辑器配置，与项目说明无关，保持未跟踪。

## 当前限制

- 关键词匹配不是向量 RAG；无租户、用户或来源权限隔离。
- 本地 JSON 不支持多进程写入。
- 本地 OAuth 签发仅适合 MVP；生产需要独立身份提供方和 TLS。
- 渠道、Agent、Memory、MCP、Evaluation 与 RBAC 仍是未启用占位。
- 模型接口没有重试、流式输出、限流或内容审计。
- pyproject.toml 的项目名仍是 uv init 默认值 `data`，`src/data/` 是未被引用的样板包；
  uv_build 只打包 `src/data`，`backend/` 不在打包范围内，当前依赖工作目录进入
  sys.path 才能导入。装到项目目录之外（例如容器）会失败，属待决策事项。
- `backend/core/`、`backend/observability/` 与 `tests/evaluation/` 是空占位，无实现。
- `frontend/` 未安装依赖、未接入后端 API；`deploy/` 的可观测性配置未启用。

## 自动结果与功能状态

F001 状态由 scripts/check.py 写入 .check_data/F001.json；功能清单只指向结果。
F002 未激活。

## 下一步

F001 交付完成后等待下一项产品决策。若继续建设知识问答，先评审并激活 F002。
