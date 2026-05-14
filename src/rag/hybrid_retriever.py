"""混合检索器：向量 + BM25 → RRF 融合。"""

from langchain_core.documents import Document


class HybridRetriever:
    """融合向量检索和 BM25 关键词检索。"""

    def __init__(self, vector_store, bm25_index, top_k: int = 5):
        self.vector_store = vector_store
        self.bm25 = bm25_index
        self.top_k = top_k
        self.vec_weight = 0.6
        self.bm25_weight = 0.4

    def retrieve(self, query: str) -> list[Document]:
        # 向量检索
        vec_results = self.vector_store.similarity_search_with_score(
            query, k=self.top_k * 2
        )

        # BM25 检索
        bm25_results = self.bm25.search(query, top_k=self.top_k * 2)

        # RRF 融合
        fused = self._rrf_fusion(vec_results, bm25_results)
        return fused[:self.top_k]

    def _rrf_fusion(self, vec_results, bm25_results, k: int = 60) -> list[Document]:
        scores: dict[str, float] = {}
        docs: dict[str, Document] = {}

        for rank, (doc, _) in enumerate(vec_results):
            key = doc.page_content[:120]
            scores[key] = scores.get(key, 0) + self.vec_weight / (k + rank + 1)
            docs[key] = doc

        for rank, (content, _, meta) in enumerate(bm25_results):
            key = content[:120]
            scores[key] = scores.get(key, 0) + self.bm25_weight / (k + rank + 1)
            if key not in docs:
                docs[key] = Document(page_content=content, metadata=meta)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [docs[key] for key, _ in ranked]

    def retrieve_with_scores(self, query: str) -> list[tuple[Document, float]]:
        docs = self.retrieve(query)
        # 返回时给一个合成分数
        return [(d, 1.0 - i * 0.1) for i, d in enumerate(docs)]