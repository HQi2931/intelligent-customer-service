from fastapi import APIRouter, Depends

from api.dependencies import get_agent_service
from api.schemas.report import ReportRequest, ReportResponse

router = APIRouter(tags=["report"])


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    req: ReportRequest,
    service=Depends(get_agent_service),
):
    """生成使用报告。"""
    result = service.generate_report(
        user_id=req.user_id,
        month=req.month,
    )
    return ReportResponse(
        report=result["report"],
        user_id=result["user_id"],
        month=result["month"],
    )
