"""Agent 核心服务 — Phase 3 多智能体编排版。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.core.cache import chat_cache
from agent.core.context_builder import ContextBuilder
from agent.core.supervisor import SupervisorAgent
from agent.core.sub_agents import SubAgentFactory
from agent.core.tool_executor import ToolExecutor
from agent.core.tool_registry import ToolRegistry
from agent.guardrails.output_guard import OutputGuardrails
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompts


class AgentService:
    """Agent 核心服务 — 支持多智能体编排 + 上下文管理 + 缓存。"""

    def __init__(self):
        self._executor = ToolExecutor()
        self._registry = ToolRegistry()
        self._supervisor = SupervisorAgent()
        self._sub_factory = SubAgentFactory(self._registry)
        self._context_builder = ContextBuilder()

        # 保留单一 Agent 作为兜底
        from langchain.agents import create_agent
        from agent.middleware.monitor import monitor_tool
        from agent.middleware.prompt_switch import log_before_model, report_prompt_switch
        from model.factory import chat_model

        self._agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=self._registry.get_all(),
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )
        logger.info("[AgentService] Phase 3 初始化完成")

    def stream_chat(
        self,
        query: str,
        session_id: str | None = None,
        history: list[dict] | None = None,
    ) -> iter:
        """流式对话 — 多智能体编排版。"""

        # 1. 缓存检查
        cached = chat_cache.get(query)
        if cached:
            logger.info("[AgentService] 缓存命中")
            yield cached
            return

        # 2. 构建上下文
        if history:
            context_messages = self._context_builder.build(history)
        else:
            context_messages = []
        context_messages.append({"role": "user", "content": query})

        # 3. 意图路由 + 子Agent执行
        route = self._supervisor.route(query)
        sub_agent = self._sub_factory.create_for_route(route)

        full_answer_parts = []

        for chunk in sub_agent.stream(
            {"messages": context_messages},
            stream_mode="values",
        ):
            latest = chunk["messages"][-1]
            if hasattr(latest, "content") and latest.content:
                text = latest.content.strip()
                if text:
                    full_answer_parts.append(text)
                    yield text

        # 4. 输出护栏
        full = "".join(full_answer_parts)
        full = OutputGuardrails.sanitize(full)

        # 5. 写入缓存
        if len(full) > 10:
            chat_cache.set(query, full)

    def generate_report(
        self, user_id: str | None = None, month: str | None = None
    ) -> dict:
        query_parts = []
        if user_id and month:
            query_parts.append(f"为用户 {user_id} 生成 {month} 的使用报告")
        elif user_id:
            query_parts.append(f"为用户 {user_id} 生成使用报告")
        else:
            query_parts.append("生成我的使用报告")
        query = "，".join(query_parts)
        results = list(self.stream_chat(query))
        return {
            "report": "\n".join(results),
            "user_id": user_id or "auto",
            "month": month or "current",
        }

    def is_ready(self) -> bool:
        return self._agent is not None

    def vector_store_ready(self) -> bool:
        try:
            health = self._registry.health_check()
            return len(health) > 0 and all(health.values())
        except Exception:
            return False

    @property
    def executor(self) -> ToolExecutor:
        return self._executor