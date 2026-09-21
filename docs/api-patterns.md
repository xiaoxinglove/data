# API 规范

以下为目标要求，现有代码尚未完整满足。

- 使用明确的请求和响应模型，限制字段类型、长度和允许值；空问题与未知渠道应明确拒绝。
- 业务 API 默认验证可信令牌及权限；认证失败与权限不足分别处理，不能只检查 Bearer 字符串存在。
- 用户身份认证采用适合部署的 OIDC 流程；不把 JWT 格式等同于完整 OAuth 实现，不默认采用密码授权模式。
- 匿名例外只有 `POST /oauth/token`：它不使用 Bearer 令牌，但必须通过
  HTTP Basic 客户端认证并限制为 `client_credentials`。
- 自动 OpenAPI、Swagger UI 和 ReDoc 在 MVP 中关闭，避免新增匿名 API 面。
- 渠道回调使用渠道要求的签名、时效与防重放验证，不强行套用交互式登录流程。
- 控制器负责协议、校验和响应映射，业务交给相应模块；错误不得泄露密钥或内部堆栈。
- 修改路由、参数、响应结构或启动方式时，同步 README.md 和 backend/api/ARCHITECTURE.md。
- 验收覆盖合法请求、无凭据、无效凭据、权限不足和输入错误。

当前资源路由是 /health、/documents、/chat、/enterprise/{channel}；令牌端点是
/oauth/token。各端点的当前行为与 scopes 见 README.md。
