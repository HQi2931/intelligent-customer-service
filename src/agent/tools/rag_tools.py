"""RAG 检索总结工具。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService

_service = RagSummarizeService()


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    """
    使用检索增强生成（RAG）方法，根据用户查询从向量存储中检索相关参考资料，并生成总结。

    参数:
    query (str): 用户的查询字符串。

    返回:
    str: 包含检索到的参考资料和总结的字符串。
    """
    return _service.rag_summarize(query)
