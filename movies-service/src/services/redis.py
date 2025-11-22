from typing import Any
import json
from redis.asyncio import Redis
from services.abstract import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        data = await self.redis.get(key)
        if not data:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def set(self, key: str, value: Any, expire: int) -> None:
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value)
        else:
            serialized = str(value)
        await self.redis.set(key, serialized, ex=expire)
