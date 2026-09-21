# RAG 模块

## 当前实现

backend/rag/pipeline.py 提供：

- retrieve(query)：固定返回空列表。
- rerank(docs)：原样返回输入。

没有解析、切分、Embedding、向量数据库、上下文构建或质量指标实现。空列表不能证明检索正常。

## 目标边界

RAG 负责有权限约束的资料解析、索引、检索、重排和上下文构建。
真实实现需定义来源追踪、无结果行为、租户隔离及 Recall@K 等可计算验收指标。
