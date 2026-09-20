# 云南林草科技服务数字化平台：后端骨架

当前仓库包含 Python / FastAPI 接口和模块占位实现。尚未形成真实知识库问答闭环，也未完成部署或端到端验收。

## 当前代码行为

| 入口 | 当前行为 | 限制 |
| --- | --- | --- |
| GET /health | 固定返回 healthy 和版本 5.7 | 未检查依赖，无认证 |
| POST /chat | 读取 query，返回 query、context、documents、status | 上下文和文档为空，无模型生成，无认证 |
| POST /enterprise/{channel} | 回显 channel，返回 accepted: true | 未分发、未验签，不代表消息处理成功 |
| data 命令 | 打印 Hello from data! | 包示例入口，不启动 API |

API 源码入口是 app/main.py。包版本是 0.1.0；API 中的 5.7 是历史硬编码，不能用作成熟度或发布证明。
当前安全模块和渠道校验恒真返回，且尚未接入 API，不能用于受信任的生产访问控制。

## 环境与运行现状

- pyproject.toml 要求 Python >=3.14，.python-version 指定 3.14。
- 使用 uv 管理项目；当前 dependencies 为空，没有 uv.lock。
- FastAPI 被源码引用但未声明依赖，ASGI 服务依赖也未配置。
- 没有 Makefile、测试套件、统一检查脚本或前端工程。

目前没有经过验证的完整安装、服务启动和验收命令。后续补齐依赖与环境后，ASGI 目标应为 app.main:app；现有 data 示例命令不是服务启动命令。环境证据见 Initialization.md。

## 目录

- app/main.py、app/api/router.py：HTTP 应用与路由。
- app/agent/kernel.py：调用 Memory、RAG 并组装占位结果。
- app/rag、app/memory、app/mcp：检索、记忆、工具占位实现。
- app/channels、app/security、app/evaluation：渠道、安全、评估占位实现。
- src/data/__init__.py：包命令示例。
- docs/：API、存储、测试规范和功能验收定义。

## 未实现能力

真实文档解析、向量检索、模型回答、持久化、OAuth/OIDC、渠道回调和评估均未完成。
当前未集成 LangGraph、CrewAI、Milvus、Neo4j 或 MySQL；这些名称不代表已选定或已实现的技术方案。

.env 是本地敏感配置文件，已由 .gitignore 忽略。当前源码没有已实现的配置加载契约，README 不列出或复制其中的值。

## 文档同步

涉及功能、接口、依赖、配置、目录或启动命令的代码变更必须同步本文件，并记录验证证据。纯内部改动不影响使用说明时，可在进度中记录无需修改的理由。
每次交付在 PROGRESS.md 记录“触发变化 → 本文件对应段落 → 核对依据与结果”。不影响用户使用的内部变化记录无需修改的理由。
这是协作交付规则；仓库尚未实现 README 自动生成或同步 CI。
实际状态见 PROGRESS.md；贡献规则见 AGENTS.md。
