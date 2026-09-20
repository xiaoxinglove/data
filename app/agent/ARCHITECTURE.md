# Agent 模块

## 当前实现

app/agent/kernel.py 提供 AgentKernel：
- 初始化 MemoryManager、RAGPipeline 和 MCPRuntime。
- run(query) 调用 memory.recall() 与 rag.retrieve(query)。
- 返回 query、context、documents 和固定 status=completed。

当前 run 没有调用 MCPRuntime、LLM、权限检查或工作流引擎；completed 仅表示函数返回，不表示任务成功。

## 当前接口

输入：字符串 query。
输出：字典。

## 目标边界

负责问答流程编排；检索、记忆、工具执行和授权分别由对应模块落实。
接入真实数据前，调用链必须传递可信用户、租户和资源范围。
