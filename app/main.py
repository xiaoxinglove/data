from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Security
from pydantic import BaseModel, Field

from app.llm import LLMError, call_glm
from app.security.oauth import require_token, token_endpoint
from app.store import DocumentStore


class DocumentInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100_000)


class ChatInput(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)


store = DocumentStore(
    Path(os.environ.get("KNOWLEDGE_BASE_PATH", "local_data/documents.json"))
)
app = FastAPI(
    title="林草知识库问答 MVP",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.post("/oauth/token", include_in_schema=False)(token_endpoint)


@app.get(
    "/health",
    dependencies=[Security(require_token, scopes=["health:read"])],
)
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/documents",
    status_code=201,
    dependencies=[Security(require_token, scopes=["documents:write"])],
)
def add_document(data: DocumentInput) -> dict[str, object]:
    document = store.add(data.title.strip(), data.content.strip())
    return {"document": document}


@app.post(
    "/chat",
    dependencies=[Security(require_token, scopes=["chat:use"])],
)
def chat(data: ChatInput) -> dict[str, object]:
    query = data.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="query 不能为空")
    documents = store.search(query)
    if not documents:
        return {"answer": "未找到相关资料", "sources": []}
    try:
        answer = call_glm(query, documents)
    except LLMError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {
        "answer": answer,
        "sources": [{"id": item["id"], "title": item["title"]} for item in documents],
    }


@app.post(
    "/enterprise/{channel}",
    dependencies=[Security(require_token, scopes=["enterprise:write"])],
)
def enterprise(channel: str) -> None:
    raise HTTPException(status_code=501, detail=f"渠道 {channel} 尚未实现")
