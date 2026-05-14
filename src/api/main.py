from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.auth import JWTAuthMiddleware
from api.middleware.error_handler import register_exception_handlers
from api.middleware.logging_mw import LoggingMiddleware
from api.middleware.ratelimit import RateLimitMiddleware
from api.routes import alerts, auth, chat, health, metrics, report, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    from api.dependencies import get_agent_service
    get_agent_service()
    yield


app = FastAPI(
    title="智能客服助手 API",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTAuthMiddleware)

register_exception_handlers(app)

app.include_router(chat.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(alerts.router)
app.include_router(auth.router)
app.include_router(sessions.router)