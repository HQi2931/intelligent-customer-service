"""Redis 滑动窗口限流中间件 — 支持多进程/多实例。"""

import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from db.redis_client import get_redis, redis_healthy

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

FALLBACK = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed 滑动窗口限流。

    Redis 不可用时回退到内存模式。
    匿名: 30 req/min, 认证: 100 req/min, 窗口: 60s
    """

    def __init__(self, app, anon_limit: int = 30, auth_limit: int = 100):
        super().__init__(app)
        self.anon_limit = anon_limit
        self.auth_limit = auth_limit
        self._window = 60.0
        self._fallback: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if (
            path in PUBLIC_PATHS
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi")
        ):
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        key = f"ratelimit:user:{user_id}" if user_id else f"ratelimit:ip:{request.client.host}"
        limit = self.auth_limit if user_id else self.anon_limit

        now = time.time()

        use_redis = redis_healthy()
        if use_redis:
            count = self._redis_check(key, now, limit)
        else:
            count = self._memory_check(key, now, limit)

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，每分钟限制 {limit} 次",
            )
        return await call_next(request)

    def _redis_check(self, key: str, now: float, limit: int) -> int:
        r = get_redis()
        cutoff = now - self._window
        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, int(self._window) + 10)
        _, count, _, _ = pipe.execute()
        return count

    def _memory_check(self, key: str, now: float, limit: int) -> int:
        window = self._fallback.setdefault(key, [])
        self._fallback[key] = [t for t in window if now - t < self._window]
        self._fallback[key].append(now)
        return len(self._fallback[key])