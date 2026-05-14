"""会话管理路由。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from api.dependencies import get_current_user, get_db
from db.models import Message, Session

router = APIRouter(tags=["sessions"], prefix="/api/sessions")


@router.get("")
def list_sessions(
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """获取当前用户的所有会话列表。"""
    sessions = (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "title": s.title,
            "message_count": len(s.messages),
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/{session_id}/messages")
def get_messages(
    session_id: str,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """获取指定会话的所有消息。"""
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in session.messages
    ]


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """删除指定会话及其所有消息。"""
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    db.delete(session)
    return {"status": "deleted", "session_id": session_id}


# ── 工具函数（供 chat 路由调用）──

def create_new_session(db: DBSession, user_id: int, title: str = "新对话") -> str:
    """创建新会话，返回 session_id。"""
    sid = uuid.uuid4().hex[:12]
    s = Session(id=sid, user_id=user_id, title=title)
    db.add(s)
    db.flush()
    return sid


def save_message(db: DBSession, session_id: str, role: str, content: str):
    """保存一条消息。"""
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)


def update_session_title(db: DBSession, session_id: str):
    """用第一条用户消息的前50字作为会话标题。"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session or session.title != "新对话":
        return
    first_msg = (
        db.query(Message)
        .filter(Message.session_id == session_id, Message.role == "user")
        .order_by(Message.created_at)
        .first()
    )
    if first_msg:
        session.title = first_msg.content[:50]
