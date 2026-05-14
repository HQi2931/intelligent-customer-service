"""告警端点 — 熔断器状态 + 错误率检测。"""

from fastapi import APIRouter, Depends

from agent.middleware.metrics import get_metrics_summary
from api.dependencies import get_agent_service

router = APIRouter(tags=["alerts"])


@router.get("/api/alerts")
async def get_alerts(service=Depends(get_agent_service)):
    alerts = []
    metrics = get_metrics_summary()

    # 检查熔断器
    for name, status in service.executor.circuit_status().items():
        if status["open"]:
            alerts.append({
                "level": "critical",
                "source": "circuit_breaker",
                "message": f"工具 {name} 已熔断",
                "detail": status,
            })

    # 检查对话失败率
    chats = metrics["chat_requests"]
    if chats["total"] > 10:
        fail_rate = chats["failed"] / chats["total"]
        if fail_rate > 0.3:
            alerts.append({
                "level": "warning",
                "source": "chat_quality",
                "message": f"对话失败率 {fail_rate:.0%} (>{30}%)",
            })

    return {
        "alerts": alerts,
        "metrics_summary": metrics,
        "circuit_status": service.executor.circuit_status(),
        "cache_size": _get_cache_size(),
    }


def _get_cache_size() -> int:
    try:
        from agent.core.cache import chat_cache
        return chat_cache.size
    except Exception:
        return 0