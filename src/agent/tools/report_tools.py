"""报告生成相关工具。"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.tools import tool

from agent.tools.data_provider import get_data_provider
from utils.logger_handler import logger


@tool(description="从外部系统中获取用户的使用记录,以字符串形式返回，如果没有记录则返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    """
    从外部系统中获取用户的使用记录。

    参数:
    user_id (str): 用户ID。
    month (str): 月份，格式为"YYYY-MM"。

    返回:
    str: 包含用户使用记录的字符串，如果没有记录则返回空字符串。
    """
    provider = get_data_provider()
    record = provider.get_user_record(user_id, month)
    if record is None:
        return ""
    return json.dumps(record, ensure_ascii=False)


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report() -> str:
    """触发中间件为报告生成场景动态注入上下文信息。"""
    logger.info("[fill_context_for_report] 上下文信息已准备，触发报告生成场景")
    return "fill_context_for_report已调用"
