"""语义分块器 — 段落/标题边界感知。"""

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


class SemanticChunker:
    """两级分块：标题结构 → 段落边界。"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ],
            strip_headers=False,
        )
        self.fallback = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n", "\n", "。", "！", "？",
                ".", "!", "?", " ", "",
            ],
        )

    def split(self, documents: list[Document]) -> list[Document]:
        result: list[Document] = []
        for doc in documents:
            md_docs = self.md_splitter.split_text(doc.page_content)
            if len(md_docs) > 1:
                for md in md_docs:
                    md.metadata.update(doc.metadata)
                result.extend(md_docs)
            else:
                result.extend(self.fallback.split_documents([doc]))
        return result