"""Redis LLM 响应缓存 — 跨重启持久化 + 跨进程共享。"""

import hashlib

from db.redis_client import get_redis, redis_healthy


class QueryCache:
    """Redis-backed 查询缓存。Redis 不可用时降级到内存。"""

    PREFIX = "cache:query:"
    DEFAULT_TTL = 1800  # 30 分钟

    def __init__(self, ttl: int = 1800):
        self.ttl = ttl
        self._memory: dict[str, str] = {}

    @staticmethod
    def _hash(query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> str | None:
        key = f"{self.PREFIX}{self._hash(query)}"

        if redis_healthy():
            val = get_redis().get(key)
            return val

        return self._memory.get(key)

    def set(self, query: str, answer: str):
        key = f"{self.PREFIX}{self._hash(query)}"

        if redis_healthy():
            get_redis().setex(key, self.ttl, answer)
        else:
            self._memory[key] = answer

    @property
    def size(self) -> int:
        if redis_healthy():
            return get_redis().dbsize()
        return len(self._memory)

    def clear(self):
        if redis_healthy():
            for k in get_redis().scan_iter(f"{self.PREFIX}*"):
                get_redis().delete(k)
        else:
            self._memory.clear()


chat_cache = QueryCache()