import time

from starlette.middleware.base import BaseHTTPMiddleware

from utils.logger_handler import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录每个 HTTP 请求的方法、路径、耗时、状态码。"""

    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info(
            f"[http] {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.1f}ms)"
        )
        return response
