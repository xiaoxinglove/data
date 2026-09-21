from backend.mcp.runtime import MCPRuntime
from backend.memory.manager import MemoryManager
from backend.rag.pipeline import RAGPipeline


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
