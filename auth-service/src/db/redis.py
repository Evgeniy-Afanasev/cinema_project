from redis.asyncio import Redis
from core.config import settings

redis: Redis | None = None


async def init_redis() -> Redis:
    """Инициализация подключения к Redis."""
    global redis
    redis = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
    return redis


async def get_redis() -> Redis:
    """Dependency для FastAPI, возвращает клиент Redis."""
    global redis
    if redis is None:
        await init_redis()
    return redis
