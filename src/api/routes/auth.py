"""用户认证路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from api.auth_utils import create_token, hash_password, verify_password
from api.dependencies import get_current_user, get_db
from api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserInfo,
)
from db.models import User

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: DBSession = Depends(get_db)):
    """用户注册。"""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        email=req.email or "",
    )
    db.add(user)
    db.flush()

    token = create_token(user.id, user.username)
    return TokenResponse(token=token, user_id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: DBSession = Depends(get_db)):
    """用户登录。"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id, user.username)
    return TokenResponse(token=token, user_id=user.id, username=user.username)


@router.get("/me", response_model=UserInfo)
def get_me(
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """获取当前用户信息。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )
