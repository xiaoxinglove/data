class RAGPipeline:
    def retrieve(self, query: str) -> list[dict[str, str]]:
        return []

    def rerank(self, docs: list[dict[str, str]]) -> list[dict[str, str]]:
        return docs
