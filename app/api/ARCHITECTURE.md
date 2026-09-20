# API 模块

## 当前实现

app/main.py 创建 FastAPI 应用：

- POST /oauth/token：HTTP Basic 客户端认证，client_credentials 签发 JWT。
- GET /health：需要 health:read。
- POST /documents：需要 documents:write，写入本地文档。
- POST /chat：需要 chat:use，检索后调用模型。
- POST /enterprise/{channel}：需要 enterprise:write，固定返回 501。

输入使用 Pydantic 模型；认证与 scope 校验由 app/security/oauth.py 提供。
OpenAPI、Swagger UI 和 ReDoc 关闭。app/api/router.py 仅保留兼容说明。
app/main.py 既可作为 ASGI 模块导入，也可作为脚本直接启动 Uvicorn。

## 边界

API 层处理协议、输入验证、安全依赖和响应映射。文档检索由 DocumentStore
完成，模型调用由 app/llm.py 完成。修改路由时同步 README 和集成测试。
