from __future__ import annotations

import json
import re
import threading
import uuid
from pathlib import Path
from typing import TypedDict


class Document(TypedDict):
    id: str
    title: str
    content: str


def _terms(text: str) -> set[str]:
    normalized = text.casefold()
    terms = set(re.findall(r"[a-z0-9]+", normalized))
    for chunk in re.findall(r"[\u4e00-\u9fff]+", normalized):
        if len(chunk) == 1:
            terms.add(chunk)
        else:
            terms.update(chunk[index : index + 2] for index in range(len(chunk) - 1))
    return terms


class DocumentStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()

    def add(self, title: str, content: str) -> Document:
        document: Document = {
            "id": uuid.uuid4().hex,
            "title": title,
            "content": content,
        }
        with self._lock:
            documents = self._load()
            documents.append(document)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            temporary.replace(self.path)
        return document

    def search(self, query: str, limit: int = 3) -> list[Document]:
        query_terms = _terms(query)
        if not query_terms:
            return []
        scored: list[tuple[int, Document]] = []
        for document in self._load():
            title_hits = len(query_terms & _terms(document["title"]))
            content_hits = len(query_terms & _terms(document["content"]))
            score = title_hits * 3 + content_hits
            if score:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in scored[:limit]]

    def _load(self) -> list[Document]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError(f"无法读取知识库文件：{self.path}") from error
        if not isinstance(data, list):
            raise RuntimeError(f"知识库文件格式错误：{self.path}")
        return data
