# 云南林草科技服务数字化平台：最小可运行 MVP

这是一个经过本地端到端验证的 FastAPI 知识问答 MVP：通过 OAuth 2.0
客户端凭据取得 JWT，写入本地文档，用关键词检索相关资料，再调用 OpenAI
兼容的模型接口生成带来源的回答。

## 已实现接口

| 接口 | Scope | 行为 |
| --- | --- | --- |
| POST /oauth/token | HTTP Basic 客户端认证 | client_credentials 换取 15 分钟 JWT |
| GET /health | health:read | 返回 status=healthy |
| POST /documents | documents:write | 写入标题和正文，返回 201 |
| POST /chat | chat:use | 检索资料；命中后调用模型，返回 answer 和 sources |
| POST /enterprise/{channel} | enterprise:write | 明确返回 501，渠道尚未实现 |

除令牌端点外，所有接口要求 Bearer JWT，并验证签发者、受众、有效期和 scope。
令牌端点通过 HTTP Basic 验证机密客户端。Swagger、ReDoc 和 OpenAPI 路由关闭。

## 环境

需要 Python 3.14 和 uv。应用不会自动读取 .env。

~~~powershell
$env:OAUTH_CLIENT_ID = "local-mvp"
$env:OAUTH_CLIENT_SECRET = "replace-with-a-client-secret"
$env:OAUTH_JWT_SECRET = "replace-with-at-least-32-random-bytes"
~~~

匹配到资料并需要生成回答时还要设置：

~~~powershell
$env:GLM_API_KEY = "your-api-key"
$env:GLM_BASE_URL = "https://api.siliconflow.cn/v1"
$env:GLM_MODEL = "zai-org/GLM-5.3"
~~~

GLM_BASE_URL 必须兼容 OpenAI 的 /chat/completions 请求结构。没有匹配资料时
不会调用模型；有匹配资料但缺少 API Key 时返回 502。

## 安装、验证与启动

~~~powershell
uv sync --locked
uv run python scripts/check.py
.\run.ps1
~~~

run.ps1 在 127.0.0.1:8008 启动服务。也可直接运行：

~~~powershell
uv run uvicorn app.main:app --host 127.0.0.1 --port 8008
~~~

获取令牌：

~~~powershell
$credentialText = "{0}:{1}" -f $env:OAUTH_CLIENT_ID, $env:OAUTH_CLIENT_SECRET
$basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentialText))
$tokenResponse = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/oauth/token -Headers @{ Authorization = "Basic $basic" } -ContentType "application/x-www-form-urlencoded" -Body "grant_type=client_credentials&scope=health%3Aread+chat%3Ause+documents%3Awrite"
$headers = @{ Authorization = "Bearer $($tokenResponse.access_token)" }
~~~

写入资料并提问：

~~~powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/documents -Headers $headers -ContentType "application/json" -Body '{"title":"森林防火","content":"严禁携带火种进入林区。"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/chat -Headers $headers -ContentType "application/json" -Body '{"query":"森林防火有哪些要求"}'
~~~

## 数据与限制

文档默认保存在 local_data/documents.json，可用 KNOWLEDGE_BASE_PATH 修改。
写入采用临时文件替换和进程内锁，不支持多进程并发写入。
检索是中文双字词及英文词的简单匹配，不是向量检索。
模型请求超时 60 秒，没有重试、流式输出或内容审计。
本地客户端凭据和 HS256 JWT 仅用于 MVP；生产部署需要独立 OAuth/OIDC
提供方、密钥轮换、TLS、限流、审计和租户隔离。

app/agent、app/rag、app/memory、app/mcp、app/channels 和 app/evaluation
仍是未启用的架构占位模块。

## 验证范围

scripts/check.py 顺序运行 Ruff、mypy strict、单元测试、API 集成测试和真实
HTTP 端到端测试。端到端使用本地假模型，不消耗真实 API Key。
通过结果写入被忽略的 .check_data/F001.json。

实际证据见 PROGRESS.md。代码影响接口、配置、依赖或命令时必须同步本文件。
