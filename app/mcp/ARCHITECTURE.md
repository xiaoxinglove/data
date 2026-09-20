# MCP 模块

## 当前实现

app/mcp/runtime.py 提供 MCPRuntime.execute(tool, args)，返回工具名和 result=None。
尚未实现注册、校验、超时或外部调用。

## 目标边界

工具运行时负责受控注册、参数验证、权限检查、超时和错误映射。
禁止任意代码执行；缺少可信身份或工具授权时默认拒绝。
