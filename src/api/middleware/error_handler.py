from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from utils.logger_handler import logger


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器。"""

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.error(
            f"[http] Unhandled exception at {request.url.path}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试"},
        )
