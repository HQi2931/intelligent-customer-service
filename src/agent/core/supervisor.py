"""Supervisor Agent — 意图分类路由器。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.factory import chat_model
from utils.logger_handler import logger


INTENT_PROMPT = """你是意图分类路由器。根据用户输入，判断属于以下哪种类型。

类型:
- knowledge: 知识问答类（选购、故障、维护、使用技巧、参数等扫地机器人相关问题）
- report: 报告生成类（要求生成使用报告、月报、查询使用记录）
- general: 通用对话类（天气查询、闲聊、问候等）

仅输出一个单词: knowledge, report, 或 general。不要解释。

用户: {query}
类型:"""


class SupervisorAgent:
    """轻量级路由器：单次 LLM 调用做意图分类。"""

    ROUTES = {
        "knowledge": "knowledge_agent",
        "report": "report_agent",
        "general": "general_agent",
    }

    def __init__(self):
        self.model = chat_model

    def route(self, query: str) -> str:
        prompt = INTENT_PROMPT.format(query=query)
        result = self.model.invoke(prompt).content.strip().lower()
        route = self.ROUTES.get(result, "general_agent")
        logger.info(f"[Supervisor] 路由: '{query[:30]}...' -> {route}")
        return route