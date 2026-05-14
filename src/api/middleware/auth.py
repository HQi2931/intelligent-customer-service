"""JWT 鉴权中间件。"""

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.auth_utils import decode_token

PUBLIC_PATHS = {
    "/api/auth/register",
    "/api/auth/login",
    "/api/health",
    "/api/metrics",
    "/api/alerts",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if (
            path in PUBLIC_PATHS
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi")
        ):
            request.state.user_id = None
            return await call_next(request)

        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(status_code=401, detail="未提供认证令牌")

        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="令牌无效或已过期")

        request.state.user_id = payload["user_id"]
        request.state.username = payload["username"]
        return await call_next(request)