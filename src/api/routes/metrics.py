"""/api/metrics 端点。"""

from fastapi import APIRouter

from agent.middleware.metrics import get_metrics_summary

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics():
    return get_metrics_summary()