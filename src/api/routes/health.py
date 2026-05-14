from fastapi import APIRouter, Depends

from api.dependencies import get_agent_service

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(service=Depends(get_agent_service)):
    return {
        "status": "ok",
        "agent_ready": service.is_ready(),
        "vector_store_ready": service.vector_store_ready(),
    }
