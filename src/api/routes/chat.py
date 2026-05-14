"""多轮对话路由 — 上下文注入 + 消息持久化 + 内容过滤。"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from agent.guardrails.content_filter import ContentFilter
from agent.middleware.metrics import record_chat_request
from api.dependencies import get_agent_service, get_current_user, get_db
from api.routes.sessions import (
    create_new_session,
    save_message,
    update_session_title,
)
from api.schemas.chat import ChatRequest
from db.models import Session

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
    service=Depends(get_agent_service),
):
    """多轮流式对话 (SSE)。"""

    # 0. 内容安全过滤
    ok, reason = ContentFilter.filter_input(req.query)
    if not ok:
        record_chat_request("blocked")
        raise HTTPException(status_code=400, detail=reason)

    # 1. 解析或创建会话
    session_id = req.session_id
    if not session_id:
        session_id = create_new_session(db, user_id)

    # 2. 验证会话归属
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.user_id == user_id)
        .first()
    )
    if not session:
        session_id = create_new_session(db, user_id)
        session = db.query(Session).filter(Session.id == session_id).first()

    # 3. 加载历史上下文
    history = [
        {"role": m.role, "content": m.content}
        for m in session.messages[-20:]
    ]

    # 4. 保存用户消息
    save_message(db, session_id, "user", req.query)
    update_session_title(db, session_id)

    # 5. 流式输出
    full_answer_parts = []

    async def event_stream():
        nonlocal full_answer_parts
        try:
            for chunk in service.stream_chat(
                query=req.query,
                session_id=session_id,
                history=history,
            ):
                if chunk:
                    full_answer_parts.append(chunk)
                    yield f"data: {chunk}\n\n"
            full_answer = "".join(full_answer_parts)
            if full_answer:
                save_message(db, session_id, "assistant", full_answer)
            record_chat_request("success")
        except Exception:
            record_chat_request("failed")
            raise
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )