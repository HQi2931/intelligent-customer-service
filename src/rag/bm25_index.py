"""BM25 关键词索引 — 与向量检索互补。"""

import os
import pickle

import jieba
from rank_bm25 import BM25Okapi


class BM25Index:
    """BM25 关键词检索，内存加载，支持持久化。"""

    def __init__(self, index_path: str = "chroma_db/bm25_index.pkl"):
        self.index_path = index_path
        self._bm25: BM25Okapi | None = None
        self._documents: list[str] = []
        self._metadatas: list[dict] = []

    def build(self, documents: list[str], metadatas: list[dict]):
        tokenized = [list(jieba.cut(doc)) for doc in documents]
        self._bm25 = BM25Okapi(tokenized)
        self._documents = documents
        self._metadatas = metadatas

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float, dict]]:
        if not self._bm25:
            return []
        tokens = list(jieba.cut(query))
        scores = self._bm25.get_scores(tokens)
        indexed = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )[:top_k]
        return [
            (self._documents[i], scores[i], self._metadatas[i])
            for i, s in indexed if s > 0
        ]

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump({
                "documents": self._documents,
                "metadatas": self._metadatas,
                "bm25": self._bm25,
            }, f)

    def load(self) -> bool:
        if not os.path.exists(self.index_path):
            return False
        with open(self.index_path, "rb") as f:
            data = pickle.load(f)
            self._documents = data["documents"]
            self._metadatas = data["metadatas"]
            self._bm25 = data["bm25"]
        return True

    @property
    def doc_count(self) -> int:
        return len(self._documents)