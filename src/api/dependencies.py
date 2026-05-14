from functools import lru_cache

from fastapi import Depends, HTTPException, Request

from db.database import SessionLocal


@lru_cache
def get_agent_service():
    """单例 AgentService，整个应用生命周期复用。"""
    from agent.core.agent_service import AgentService
    return AgentService()


def get_db():
    """FastAPI 依赖：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_current_user(request: Request) -> int:
    """FastAPI 依赖：从请求中提取当前用户 ID。"""
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="未登录")
    return user_id
