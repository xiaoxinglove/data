from app.mcp.runtime import MCPRuntime
from app.memory.manager import MemoryManager
from app.rag.pipeline import RAGPipeline


class AgentKernel:
    def __init__(self) -> None:
        self.memory = MemoryManager()
        self.rag = RAGPipeline()
        self.tools = MCPRuntime()

    def run(self, query: str) -> dict[str, object]:
        context = self.memory.recall()
        docs = self.rag.retrieve(query)
        return {
            "query": query,
            "context": context,
            "documents": docs,
            "status": "completed",
        }
