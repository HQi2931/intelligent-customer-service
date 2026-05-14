"""子 Agent 工厂 — 按意图创建精简 Agent。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain.agents import create_agent

from agent.middleware.monitor import monitor_tool
from agent.middleware.prompt_switch import log_before_model
from model.factory import chat_model
from utils.logger_handler import logger


KNOWLEDGE_SYSTEM = """你是扫地机器人专业知识助手。你必须使用 rag_summarize 工具检索知识库来回答问题。

规则:
1. 必须调用 rag_summarize 工具
2. 仅基于检索到的参考资料回答
3. 如果检索结果不足以回答，说"我目前没有这方面的资料"
4. 回答要简洁专业"""

REPORT_SYSTEM = """你是报告生成专家。严格按流程生成使用报告。

流程:
1. 调用 get_user_id 获取用户ID
2. 调用 get_current_month 获取当前月份
3. 调用 fill_context_for_report 准备上下文
4. 调用 fetch_external_data 获取使用数据
5. 如需专业建议，可调用 rag_summarize 补充

规则: 不要调用 get_weather 或 get_user_location"""

GENERAL_SYSTEM = """你是通用智能助手。可以查询天气和用户位置信息。

工具:
- get_weather: 查询城市天气
- get_user_location: 获取用户位置
- rag_summarize: 检索专业知识（仅在用户明确询问扫地机器人相关问题时使用）"""


class SubAgentFactory:
    """按需创建精简子 Agent。"""

    def __init__(self, tool_registry):
        self.model = chat_model
        self.registry = tool_registry

    def create_knowledge_agent(self):
        return create_agent(
            model=self.model,
            system_prompt=KNOWLEDGE_SYSTEM,
            tools=[self.registry.get_tool("rag_summarize")],
            middleware=[monitor_tool, log_before_model],
        )

    def create_report_agent(self):
        return create_agent(
            model=self.model,
            system_prompt=REPORT_SYSTEM,
            tools=[
                self.registry.get_tool("get_user_id"),
                self.registry.get_tool("get_current_month"),
                self.registry.get_tool("fill_context_for_report"),
                self.registry.get_tool("fetch_external_data"),
                self.registry.get_tool("rag_summarize"),
            ],
            middleware=[monitor_tool, log_before_model],
        )

    def create_general_agent(self):
        return create_agent(
            model=self.model,
            system_prompt=GENERAL_SYSTEM,
            tools=[
                self.registry.get_tool("get_weather"),
                self.registry.get_tool("get_user_location"),
                self.registry.get_tool("rag_summarize"),
            ],
            middleware=[monitor_tool, log_before_model],
        )

    def create_for_route(self, route: str):
        if route == "knowledge_agent":
            return self.create_knowledge_agent()
        elif route == "report_agent":
            return self.create_report_agent()
        else:
            return self.create_general_agent()