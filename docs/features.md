# 功能与验收清单

需求和验收契约人工维护；验证器维护 .check_data/F001.json 等自动结果。
源码变化后旧结果仅是历史证据。

| 编号 | 功能 | 工作状态 | 自动验证结果 |
| --- | --- | --- | --- |
| F001 | 最小服务运行闭环 | MVP 已实现 | 见 .check_data/F001.json |
| F002 | 真实知识问答 | 未激活 | 无 |

## F001 已实现契约

- 安装：uv sync --locked。
- 启动：uv run uvicorn app.main:app --host 127.0.0.1 --port 8008。
- 完整验证：uv run python scripts/check.py。
- /oauth/token 仅接受 HTTP Basic 客户端认证和 client_credentials。
- 资源接口分别验证所需 scope。
- 缺失或无效令牌返回 401；scope 不足返回 403。
- /chat 缺失、空白或非字符串 query 返回 422。
- /enterprise/{channel} 返回 501。
- 验证器失败时停止且不写 passing；全部检查通过才写结果。

## F002 验收方向

当前关键词检索和模型调用只构成 MVP，不等同于真实 RAG。
激活前确定资料集、来源追踪、租户隔离、Recall@K、回答忠实度和阈值。
