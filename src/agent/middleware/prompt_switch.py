"""Prompt 切换中间件。"""

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain.agents.middleware import before_model, dynamic_prompt

from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@before_model
def log_before_model(state: Any, runtime: Any) -> None:
    """模型执行前记录状态。"""
    logger.info("[log_before_model] Model execution starting")
    try:
        logger.debug(f"[log_before_model] state: {state}")
        logger.debug(f"[log_before_model] runtime: {runtime}")
    except Exception as exc:
        logger.warning(
            f"[log_before_model] Failed to log model state: {exc}",
            exc_info=True,
        )
    finally:
        logger.info("[log_before_model] Model execution pre-log complete")


@dynamic_prompt
def report_prompt_switch(request) -> str:
    """根据上下文切换到报告生成 Prompt。"""
    context = getattr(request.runtime, "context", {}) or {}
    if context.get("report"):
        logger.info("[report_prompt_switch] Using report prompt")
        return load_report_prompts()
    return load_system_prompts()
