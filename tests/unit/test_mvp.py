from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.main import ChatInput, chat
from backend.store import DocumentStore


class DocumentStoreUnitTests(unittest.TestCase):
    def test_write_and_retrieve_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = DocumentStore(Path(directory) / "documents.json")
            written = store.add("云南松病虫害", "云南松需要监测松毛虫并及时防治。")
            results = store.search("云南松松毛虫如何防治")
        self.assertEqual(results[0]["id"], written["id"])


class ChatTests(unittest.TestCase):
    def test_returns_sources_for_matching_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_store = DocumentStore(Path(directory) / "documents.json")
            written = test_store.add("森林防火", "进入林区严禁携带火种。")
            with (
                patch("backend.main.store", test_store),
                patch("backend.main.call_glm", return_value="应禁止携带火种。") as llm,
            ):
                result = chat(ChatInput(query="森林防火有哪些要求"))
        self.assertEqual(result["answer"], "应禁止携带火种。")
        self.assertEqual(
            result["sources"], [{"id": written["id"], "title": "森林防火"}]
        )
        llm.assert_called_once()

    def test_no_match_does_not_call_llm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_store = DocumentStore(Path(directory) / "documents.json")
            test_store.add("森林防火", "进入林区严禁携带火种。")
            with (
                patch("backend.main.store", test_store),
                patch("backend.main.call_glm") as llm,
            ):
                result = chat(ChatInput(query="海洋潮汐观测"))
        self.assertEqual(result, {"answer": "未找到相关资料", "sources": []})
        llm.assert_not_called()


if __name__ == "__main__":
    unittest.main()
