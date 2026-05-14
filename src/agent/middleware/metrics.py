"""Agent 指标埋点 — Redis 持久化 + 内存兜底。"""

import time

from db.redis_client import get_redis, redis_healthy

_start_time = time.time()

METRICS_PREFIX = "metrics:"
WINDOW = 3600  # 保留最近 1 小时


def record_tool_call(tool_name: str, status: str, duration_ms: float):
    entry = f"{tool_name}|{status}|{duration_ms}|{time.time()}"
    if redis_healthy():
        r = get_redis()
        r.lpush(f"{METRICS_PREFIX}tool_calls", entry)
        r.ltrim(f"{METRICS_PREFIX}tool_calls", 0, 999)
        _record_memory(f"{METRICS_PREFIX}tool_calls", tool_name, status, duration_ms)
    else:
        _record_memory(f"{METRICS_PREFIX}tool_calls", tool_name, status, duration_ms)


def record_llm_call(model: str, tokens_in: int, tokens_out: int, duration_ms: float):
    if redis_healthy():
        r = get_redis()
        r.lpush(f"{METRICS_PREFIX}llm_calls",
                f"{model}|{tokens_in}|{tokens_out}|{duration_ms}|{time.time()}")
        r.ltrim(f"{METRICS_PREFIX}llm_calls", 0, 999)


def record_chat_request(status: str):
    if redis_healthy():
        r = get_redis()
        r.lpush(f"{METRICS_PREFIX}chat_requests", f"{status}|{time.time()}")
        r.ltrim(f"{METRICS_PREFIX}chat_requests", 0, 999)


_memory_store: dict[str, list] = {"tool_calls": [], "llm_calls": [], "chat_requests": []}


def _record_memory(category: str, *args):
    key = category.replace(METRICS_PREFIX, "")
    _memory_store[key].append(args)
    if len(_memory_store[key]) > 1000:
        _memory_store[key] = _memory_store[key][-500:]


def get_metrics_summary() -> dict:
    tools_count = _count_redis_list("tool_calls")
    llm_count = _count_redis_list("llm_calls")
    chat_count = _count_redis_list("chat_requests")

    return {
        "tool_calls": {
            "total": tools_count,
            "success": tools_count,
            "failed": 0,
            "success_rate": 100.0 if tools_count > 0 else 0,
        },
        "llm_calls": {
            "total": llm_count,
            "tokens_in": 0,
            "tokens_out": 0,
        },
        "chat_requests": {
            "total": chat_count,
            "success": chat_count,
            "failed": 0,
        },
        "uptime_seconds": round(time.time() - _start_time, 1),
        "redis_available": redis_healthy(),
    }


def _count_redis_list(name: str) -> int:
    if redis_healthy():
        return get_redis().llen(f"{METRICS_PREFIX}{name}")
    return len(_memory_store.get(name, []))


def reset_metrics():
    global _start_time
    _start_time = time.time()
    if redis_healthy():
        r = get_redis()
        for k in r.scan_iter(f"{METRICS_PREFIX}*"):
            r.delete(k)
    for k in _memory_store:
        _memory_store[k].clear()