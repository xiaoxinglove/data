# API 模块

## 当前实现

app/main.py 创建 FastAPI 应用并注册 app/api/router.py。

当前路由：

- GET /health：固定返回状态和版本。
- POST /chat：接收未建模的 dict，调用 AgentKernel.run。
- POST /enterprise/{channel}：回显 channel 并固定接受。

三个路由均未认证，输入和响应没有 Pydantic 模型。

## 目标边界

API 层负责 HTTP 协议、输入校验、认证依赖和响应映射；业务逻辑交给模块。
修改路由或使用方式时同步 README.md，并按 docs/api-patterns.md 验证成功及拒绝路径。
