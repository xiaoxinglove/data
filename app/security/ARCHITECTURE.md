# Security 模块

## 当前实现

app/security/oauth.py 实现最小 OAuth 2.0 客户端凭据流程：

- /oauth/token 通过 HTTP Basic 验证机密客户端。
- 仅接受 client_credentials 和预定义 scopes。
- 使用 HS256 签发 15 分钟 JWT。
- 资源端验证签发者、受众、有效期和 scope。
- 缺失或无效令牌返回 401，scope 不足返回 403。
- OAuth 配置缺失时返回 503。

客户端与 JWT 密钥由环境变量提供。RBAC.check 仍是未接入的恒真占位。

## 边界

本地签发方案用于单实例 MVP。生产环境应使用独立 OAuth/OIDC 提供方、
客户端注册、密钥轮换、TLS、撤销和审计。
