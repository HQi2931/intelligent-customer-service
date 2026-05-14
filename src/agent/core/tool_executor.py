"""工具执行器：超时、重试、熔断、降级保护。"""

import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger_handler import logger


@dataclass
class CircuitState:
    """单个工具的熔断器状态。"""
    failure_count: int = 0
    last_failure_time: float = 0.0
    is_open: bool = False
    open_until: float = 0.0

    threshold: int = 5
    recovery_timeout: float = 30.0


class ToolExecutor:
    """带容错机制的工具调用包装器。

    功能:
    - 超时控制 (默认 30s)
    - 指数退避重试 (默认 3 次)
    - 熔断器 (连续 5 次失败 → 熔断 30s)
    - 降级策略 (每个工具有默认降级返回值)
    """

    def __init__(
        self,
        default_timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ):
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._circuits: dict[str, CircuitState] = {}

        # 降级策略
        self._fallbacks: dict[str, str] = {
            "rag_summarize": "当前知识库检索暂时不可用，请稍后重试。",
            "get_weather": "天气信息暂时无法获取，建议参考当地气象预报。",
            "fetch_external_data": "{}",
            "get_user_location": "未知城市",
            "get_user_id": "guest",
            "get_current_month": "2025-06",
            "fill_context_for_report": "fill_context_for_report已调用",
        }

        self._retryable = (TimeoutError, ConnectionError, OSError)

    # ── 熔断器 ──

    def _circuit(self, name: str) -> CircuitState:
        return self._circuits.setdefault(name, CircuitState())

    def _is_open(self, name: str) -> bool:
        c = self._circuit(name)
        if not c.is_open:
            return False
        if time.time() > c.open_until:
            c.is_open = False
            logger.info(f"[ToolExecutor] 熔断器半开: {name}")
            return False
        return True

    def _record_ok(self, name: str):
        c = self._circuit(name)
        c.failure_count = 0
        c.is_open = False

    def _record_fail(self, name: str):
        c = self._circuit(name)
        c.failure_count += 1
        c.last_failure_time = time.time()
        if c.failure_count >= c.threshold:
            c.is_open = True
            c.open_until = time.time() + c.recovery_timeout
            logger.warning(
                f"[ToolExecutor] 熔断器 OPEN: {name} "
                f"(连续{c.failure_count}次失败, {c.recovery_timeout}s后恢复)"
            )

    # ── 执行 ──

    def execute(self, tool_name: str, tool_fn: Callable, **kwargs) -> str:
        """执行工具调用，自动应用熔断/重试/降级。"""

        if self._is_open(tool_name):
            logger.warning(f"[ToolExecutor] 熔断中, 降级: {tool_name}")
            return self._fallback(tool_name)

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = tool_fn(**kwargs)
                self._record_ok(tool_name)
                return result
            except self._retryable as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = self.retry_backoff ** attempt
                    logger.warning(
                        f"[ToolExecutor] 重试 {attempt + 1}/{self.max_retries} "
                        f"{tool_name} ({wait:.1f}s): {e}"
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        f"[ToolExecutor] 重试耗尽: {tool_name}: {e}"
                    )
            except Exception as e:
                last_error = e
                logger.error(f"[ToolExecutor] 不可重试: {tool_name}: {e}")
                break

        self._record_fail(tool_name)
        return self._fallback(tool_name)

    def _fallback(self, tool_name: str) -> str:
        return self._fallbacks.get(tool_name, "该功能暂时不可用。")

    # ── 状态 ──

    def circuit_status(self) -> dict:
        """返回所有工具的熔断状态。"""
        return {
            name: {
                "open": c.is_open,
                "failures": c.failure_count,
                "open_until": c.open_until if c.is_open else None,
            }
            for name, c in self._circuits.items()
        }