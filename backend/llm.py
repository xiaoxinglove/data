from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parents[1]
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(ROOT_DIR)) 



from backend.store import Document
    

DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "zai-org/GLM-5.3"


class LLMError(RuntimeError):
    pass


def call_glm(question: str, documents: Sequence[Document]) -> str:
    api_key = os.environ.get("GLM_API_KEY", "").strip()
    if not api_key:
        raise LLMError("未设置 GLM_API_KEY")
    base_url = os.environ.get("GLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("GLM_MODEL", DEFAULT_MODEL)
    context = "\n\n".join(
        f"来源：{item['title']}\n{item['content']}" for item in documents
    )
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是林草科技资料助手。只能依据给定资料回答；"
                        "资料不足时明确说明。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"资料：\n{context}\n\n问题：{question}",
                },
            ],
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise LLMError("模型返回空答案")
        return content.strip()
    except urllib.error.HTTPError as error:
        raise LLMError(f"模型服务返回 HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise LLMError("无法连接模型服务") from error
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise LLMError("模型响应格式错误") from error
