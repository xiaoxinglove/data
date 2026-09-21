# Forestry AI Knowledge Platform

云南林草科技服务数字化平台的智能知识问答后端。

当前版本是可运行、可验证的 MVP。它已经完成 OAuth 2.0 保护、本地知识写入、
关键词检索和模型问答闭环。企业级 RAG、Agent 编排、渠道接入、可观测性和
多租户能力属于后续规划，不能视为当前已实现能力。

---

## 1. 项目概述

### 1.1 项目定位

本项目面向林草科技服务场景，目标是连接业务资料、模型能力和企业服务渠道，
逐步形成可追溯、可扩展、可审计的知识服务平台。

当前 MVP 提供：

- 机密客户端取得短期访问令牌；
- 受保护的健康检查、资料写入和问答接口；
- 本地 JSON 文档存储；
- 中文双字词及英文词关键词检索；
- OpenAI Compatible 模型调用；
- 回答来源返回；
- 单元、集成和真实 HTTP 端到端验证。

### 1.2 当前成熟度

| 维度 | 当前状态 |
| --- | --- |
| 服务运行 | 已实现并通过端到端验证 |
| API 鉴权 | OAuth 2.0 client_credentials MVP |
| 知识存储 | 本地 JSON，单进程写入 |
| 检索 | 关键词匹配 |
| 模型调用 | OpenAI Compatible Chat Completions |
| Agent / Workflow | 架构占位，未接入 |
| 向量 RAG / Knowledge Graph | 未实现 |
| 企业微信 / 飞书 | 未实现，接口明确返回 501 |
| 可观测性 / 多租户 | 未实现 |
| 生产部署 | 未完成 |

---

## 2. 项目目标与设计原则

### 2.1 演进目标

项目计划从当前知识问答 MVP 逐步演进为企业级林草知识与智能服务平台，支持：

- 企业知识统一接入；
- 可追溯智能问答；
- 文档理解与结构化处理；
- 检索质量评估；
- Agent 工作流；
- 企业协作渠道；
- 权限隔离与审计。

以上是演进方向，具体功能只有通过功能清单与验证器后才算完成。

### 2.2 设计原则

1. **证据优先**：代码、测试和可复验结果高于文档描述。
2. **安全默认拒绝**：资源接口必须验证令牌与 scope。
3. **逐层验收**：单元、集成、端到端按顺序通过。
4. **来源可追踪**：回答返回命中文档来源。
5. **最小闭环**：没有验收需求时不提前引入复杂基础设施。
6. **目标与现状分离**：规划架构不得写成已实现能力。

---

## 3. 系统架构

### 3.1 当前 MVP 架构

~~~text
机密客户端
   |
   | HTTP Basic + client_credentials
   v
POST /oauth/token
   |
   | Bearer JWT + scopes
   v
FastAPI
   |
   +-- GET  /health
   +-- POST /documents ------> local_data/documents.json
   +-- POST /chat
   |        |
   |        +--> 关键词检索
   |        +--> OpenAI Compatible LLM
   |        +--> answer + sources
   |
   +-- POST /enterprise/{channel} -> 501
~~~

### 3.2 目标架构方向

~~~text
用户与企业渠道
       |
    API Layer
       |
身份、权限、租户边界
       |
Agent / Workflow Runtime
       |
--------------------------------
| Knowledge Pipeline           |
| Retrieval / Reranking        |
| Context / Source Trace       |
--------------------------------
       |
企业数据与模型服务
~~~

目标架构中的 Agent、向量数据库、图数据库、缓存和任务队列尚未选型完成。
选型必须以数据规模、检索基准、部署条件和运维成本为依据。

---

## 4. 技术栈

### 4.1 当前采用

| 类别 | 技术 |
| --- | --- |
| 语言 | Python 3.14 |
| Web | FastAPI、Uvicorn |
| 数据模型 | Pydantic |
| OAuth Token | PyJWT、HS256 |
| 存储 | JSON 文件 |
| 检索 | 标准库正则与关键词评分 |
| 模型 | OpenAI Compatible HTTP API |
| HTTP 客户端 | Python urllib |
| 包管理 | uv、uv.lock |
| 测试 | pytest、FastAPI TestClient、本地 HTTP 端到端 |
| 质量 | Ruff、mypy strict |

### 4.2 尚未采用

LangGraph、Milvus、Neo4j、MySQL、Redis、MinIO、Celery、Prometheus 和
Grafana 当前都不是运行依赖。后续引入必须先形成决策记录和验收标准。

---

## 5. 核心模块

### 5.1 API

backend/main.py 提供令牌、健康检查、资料写入、问答和渠道占位接口。
请求模型负责输入边界，安全依赖负责 JWT 和 scope 校验。

### 5.2 Security

backend/security/oauth.py 实现本地 OAuth 2.0 客户端凭据闭环：

- HTTP Basic 客户端认证；
- 15 分钟 JWT；
- issuer、audience、expiry 校验；
- scope 授权；
- 401、403、503 错误边界。

该实现适合单实例 MVP。生产环境应使用独立 OAuth/OIDC 提供方、TLS、
密钥轮换和审计。

### 5.3 Document Store

backend/store.py 将文档写入本地 JSON 文件，使用进程内锁和临时文件替换降低
单进程写入损坏风险。它不支持多进程并发、数据库事务或租户隔离。

### 5.4 Retrieval

当前检索按标题和正文的关键词命中计分，标题权重更高，最多返回三份资料。
它不是 Embedding、向量检索、Hybrid RAG 或 GraphRAG。

### 5.5 LLM

backend/llm.py 调用 OpenAI Compatible 的 /chat/completions 接口。系统提示要求
只依据检索资料回答；模型错误转换为明确的 API 错误。

### 5.6 架构占位模块

backend/agent、backend/rag、backend/memory、backend/mcp、backend/channels 和 backend/evaluation
尚未接入 MVP 主链路。目录存在不代表功能已经完成。

---

## 6. API 概览

| 方法与路径 | 鉴权要求 | 当前结果 |
| --- | --- | --- |
| POST /oauth/token | HTTP Basic | 签发 client_credentials JWT |
| GET /health | health:read | status=healthy |
| POST /documents | documents:write | 201 与文档对象 |
| POST /chat | chat:use | answer 与 sources |
| POST /enterprise/{channel} | enterprise:write | 501 Not Implemented |

Swagger、ReDoc 和 OpenAPI 路由在 MVP 中关闭。详细输入、错误和示例以测试及
backend/main.py 为准。

---

## 7. 项目结构

~~~text
Forest Production Platform/
├── AGENTS.md                  项目协作总则
├── CONSTRAINTS.md             约束索引
├── DECISIONS.md               架构决策
├── PROGRESS.md                进度、验证和文档代码同步台账
├── README.md                  项目总说明手册
├── Initialization.md          环境核查入口
├── pyproject.toml             依赖与工具配置
├── uv.lock                    锁定依赖
├── run.ps1                    Windows 启动与验证入口
├── backend/
│   ├── main.py                FastAPI 应用（当前 MVP 主链路）
│   ├── store.py               本地文档存储与检索
│   ├── llm.py                 模型适配
│   ├── security/oauth.py      OAuth 2.0 与 JWT
│   ├── agent/ api/ channels/ evaluation/ mcp/ memory/ rag/
│   │                          未接入主链路的占位模块
│   ├── core/ observability/   空目录，仅占位
│   └── */ARCHITECTURE.md      模块边界
├── scripts/
│   ├── check.py               顺序验证器
│   └── http_check.py          真实 HTTP 端到端验证
├── tests/
│   ├── unit/                  4 个单元测试
│   ├── integration/           6 个集成测试
│   ├── security/              11 个 OAuth 安全测试
│   └── evaluation/            占位目录，无用例
├── frontend/                  Vue + Vite 骨架，未安装依赖、未接入后端 API
├── deploy/                    Prometheus / Loki / Grafana 配置骨架，未启用
├── src/                       uv init 残留样板包，未被应用引用
└── docs/
    ├── features.md
    ├── api-patterns.md
    ├── database-rules.md
    └── testing-standards.md
~~~

---

## 8. 环境配置

### 8.1 必需环境

- Python 3.14；
- uv；
- PowerShell 用于 run.ps1。

应用不会自动读取 .env。环境变量示例见 .env.example。

### 8.2 OAuth 配置

~~~powershell
$env:OAUTH_CLIENT_ID = "local-mvp"
$env:OAUTH_CLIENT_SECRET = "replace-with-a-client-secret"
$env:OAUTH_JWT_SECRET = "replace-with-at-least-32-random-bytes"
~~~

### 8.3 模型配置

~~~powershell
$env:GLM_API_KEY = "your-api-key"
$env:GLM_BASE_URL = "https://api.siliconflow.cn/v1"
$env:GLM_MODEL = "zai-org/GLM-5.3"
~~~

有命中文档但缺少模型 API Key 时，问答接口返回 502。无命中文档时不调用模型。

---

## 9. 安装、验证与启动

### 9.1 安装

~~~powershell
uv sync --locked
~~~

### 9.2 完整验证

~~~powershell
uv run python scripts/check.py
~~~

验证器依次执行：

1. Ruff；
2. mypy strict；
3. 单元测试；
4. 集成测试；
5. 真实 Uvicorn HTTP 端到端测试。

自动结果写入 .check_data/F001.json。

### 9.3 启动

~~~powershell
.\run.ps1
~~~

默认地址：http://127.0.0.1:8008

也可以直接执行入口文件：

~~~powershell
$env:APP_HOST = "127.0.0.1"
$env:APP_PORT = "8008"
python backend/main.py
~~~

`APP_HOST` 和 `APP_PORT` 可选，默认值分别为 `127.0.0.1` 和 `8008`。
执行所用的 Python 环境必须已安装项目依赖。

也可以直接运行：

~~~powershell
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8008
~~~

---

## 10. 调用示例

### 10.1 获取令牌

~~~powershell
$credentialText = "{0}:{1}" -f $env:OAUTH_CLIENT_ID, $env:OAUTH_CLIENT_SECRET
$basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentialText))
$tokenResponse = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/oauth/token -Headers @{ Authorization = "Basic $basic" } -ContentType "application/x-www-form-urlencoded" -Body "grant_type=client_credentials&scope=health%3Aread+chat%3Ause+documents%3Awrite"
$headers = @{ Authorization = "Bearer $($tokenResponse.access_token)" }
~~~

### 10.2 写入资料并提问

~~~powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/documents -Headers $headers -ContentType "application/json" -Body '{"title":"森林防火","content":"严禁携带火种进入林区。"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/chat -Headers $headers -ContentType "application/json" -Body '{"query":"森林防火有哪些要求"}'
~~~

---

## 11. 安全设计

当前已实现：

- 机密客户端认证；
- Bearer JWT；
- 访问令牌过期时间；
- issuer 与 audience；
- scope 权限；
- 密钥来自环境变量；
- 密钥文件和本地知识数据不进入 Git。

当前未实现：

- TLS 终止；
- 外部身份提供方；
- 用户登录和 RBAC；
- 多租户数据隔离；
- 密钥轮换与撤销；
- 限流与审计；
- Prompt Injection 防护。

client_credentials 只适用于机密客户端及预先授权的资源范围，生产部署必须
通过 TLS 传输令牌。协议依据见 [RFC 6749 第 4.4 节](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4)。

---

## 12. 可观测性与运维

当前只有进程输出和验证结果，没有结构化日志、Metrics 或 Trace。

后续可观测性至少应覆盖：

- request_id；
- client_id 或主体标识；
- 路由、状态码和耗时；
- 检索结果数量；
- 模型耗时与 token usage；
- 错误类别；
- 敏感字段脱敏。

Prometheus、Grafana 和 OpenTelemetry 尚未接入。

---

## 13. 开发与交付规范

- 项目规则见 AGENTS.md；
- 架构决策见 DECISIONS.md；
- 当前进度、验证证据以及代码与文档同步关系见 PROGRESS.md；
- 功能验收见 docs/features.md；
- API 规范见 docs/api-patterns.md；
- 测试规范见 docs/testing-standards.md。

每次项目迭代都必须核对并更新本手册，使当前能力、架构、接口、依赖、配置、
运行方式、安全边界、限制和路线与交付代码一致。同步过程、核对依据和无需修改
的原因统一记录在 PROGRESS.md，本手册不堆叠变化日志。

提交消息使用 feat、fix、docs、refactor、test 等清晰前缀。
功能完成以端到端验证通过为准。

---

## 14. 版本与路线

### 0.1 MVP：当前版本

- OAuth 2.0 保护；
- 本地文档写入；
- 关键词检索；
- 模型回答及来源；
- 自动分层验证。

### F002：候选下一阶段

- 正式资料集与解析流程；
- 来源定位与引用；
- 检索基准集；
- 向量或混合检索的证据驱动选型；
- 回答忠实度评估；
- 租户和资料权限边界。

### 后续方向

Agent 工作流、企业渠道、知识图谱、长期记忆和完整可观测性需独立立项，
不能以目录或空接口代替实现。

---

## 15. 已知限制

- 仅适合单实例开发与验证；
- 本地 JSON 不支持多进程写入；
- 关键词检索能力有限；
- 同步模型请求可能阻塞工作线程；
- 没有数据迁移和备份机制；
- 没有真实模型服务的自动验收；
- 测试客户端当前产生两条上游弃用警告。

这些限制及其后续处理状态统一维护在 PROGRESS.md。
