
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model


class RagSummarizeService:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.retriever = self.vector_store_service.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.chat_model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        return self.prompt_template | self.chat_model | StrOutputParser()

    def retrieve_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retrieve_docs(query)
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】参考资料：{doc.page_content}|参考元数据：{doc.metadata}"

        return self.chain.invoke(
            {
                "input": query,
                "context": context
            }
        )

if __name__ == "__main__":
    service = RagSummarizeService()
    query = "小户型适合哪种扫地机器人？"
    result = service.rag_summarize(query)
    print(result)
