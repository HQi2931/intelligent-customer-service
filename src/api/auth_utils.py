"""认证工具：密码哈希、JWT 签发/验证。"""

import hashlib
import os
import time

import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production-2026")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """SHA-256 + salt 哈希。"""
    salt = os.urandom(16).hex()
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码。"""
    salt, target = password_hash.split(":", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == target


def create_token(user_id: int, username: str) -> str:
    """生成 JWT token。"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + TOKEN_EXPIRE_HOURS * 3600,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """解析 JWT token，失败返回 None。"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
