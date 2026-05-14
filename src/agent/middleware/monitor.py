"""工具调用监控中间件 — 记录耗时并上报指标。"""

import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from agent.middleware.metrics import record_tool_call
from utils.logger_handler import logger


@wrap_tool_call()
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
) -> ToolMessage | Command[Any]:
    """监控工具调用：记录耗时、参数、失败信息，上报指标。"""
    tool_call = request.tool_call
    tool_name = (
        tool_call.get("name")
        if isinstance(tool_call, dict)
        else getattr(tool_call, "name", "<unknown>")
    )
    tool_args = (
        tool_call.get("args")
        if isinstance(tool_call, dict)
        else getattr(tool_call, "args", None)
    )

    logger.info(f"[monitor_tool] Start: {tool_name}, args: {tool_args}")
    start = time.time()

    try:
        result = handler(request)
        duration = (time.time() - start) * 1000
        logger.info(f"[monitor_tool] Done: {tool_name} ({duration:.1f}ms)")
        record_tool_call(tool_name, "success", duration)
        return result
    except Exception as exc:
        duration = (time.time() - start) * 1000
        logger.error(
            f"[monitor_tool] Failed: {tool_name} ({duration:.1f}ms): {exc}",
            exc_info=True,
        )
        record_tool_call(tool_name, "failed", duration)
        raise