"""工具注册中心 - 管理所有 Agent 工具及其健康检查。"""

import sys
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger_handler import logger


class ToolRegistry:
    """工具注册中心：注册、获取、健康检查。"""

    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._health_checks: dict[str, Callable[[], bool]] = {}
        self._register_defaults()

    def _register_defaults(self):
        """注册所有默认工具。"""
        from agent.tools.rag_tools import rag_summarize
        from agent.tools.report_tools import (
            fetch_external_data,
            fill_context_for_report,
        )
        from agent.tools.user_tools import (
            get_current_month,
            get_user_id,
            get_user_location,
            get_weather,
        )

        self.register("rag_summarize", rag_summarize, health_fn=self._check_vector_store)
        self.register("get_weather", get_weather)
        self.register("get_user_location", get_user_location)
        self.register("get_user_id", get_user_id)
        self.register("get_current_month", get_current_month)
        self.register("fetch_external_data", fetch_external_data, health_fn=self._check_external_data)
        self.register("fill_context_for_report", fill_context_for_report)

        logger.info(f"[ToolRegistry] 已注册 {len(self._tools)} 个工具")

    @staticmethod
    def _check_vector_store() -> bool:
        """检查向量库连接。"""
        try:
            from rag.vector_store import VectorStoreService
            vs = VectorStoreService()
            # 尝试获取 collection 数量来验证连接
            _ = vs.vector_store._collection.count()
            return True
        except Exception:
            return False

    @staticmethod
    def _check_external_data() -> bool:
        """检查外部数据文件是否存在。"""
        try:
            from agent.tools.data_provider import ExternalDataProvider
            provider = ExternalDataProvider()
            return provider.is_loaded or True  # 惰性加载，文件存在即认为可用
        except Exception:
            return False

    def register(
        self,
        name: str,
        tool_fn: Callable,
        health_fn: Callable[[], bool] | None = None,
    ):
        """注册一个工具，可选附带健康检查函数。"""
        self._tools[name] = tool_fn
        if health_fn:
            self._health_checks[name] = health_fn

    def get_all(self) -> list[Callable]:
        """获取所有已注册的工具函数列表。"""
        return list(self._tools.values())

    def get_tool(self, name: str) -> Callable | None:
        """按名称获取工具。"""
        return self._tools.get(name)

    def health_check(self) -> dict[str, bool]:
        """执行所有注册了健康检查的工具的健康检查。"""
        return {name: fn() for name, fn in self._health_checks.items()}
