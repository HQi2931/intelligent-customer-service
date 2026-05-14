"""Redis 连接管理 — 单例 + 健康检查。"""

import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_pool: redis.ConnectionPool | None = None
_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """获取 Redis 客户端单例。"""
    global _pool, _client
    if _client is None:
        _pool = redis.ConnectionPool.from_url(
            REDIS_URL,
            max_connections=20,
            decode_responses=True,
        )
        _client = redis.Redis(connection_pool=_pool)
    return _client


def redis_healthy() -> bool:
    """检查 Redis 连接是否正常。"""
    try:
        return get_redis().ping()
    except Exception:
        return False


def close_redis():
    """关闭连接池。"""
    global _pool, _client
    if _pool:
        _pool.disconnect()
    _pool = None
    _client = None