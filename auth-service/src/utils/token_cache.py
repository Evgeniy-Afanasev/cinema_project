from db.redis import get_redis
from core.config import settings

ACCESS_TTL = settings.access_token_exp_minutes * 60
REFRESH_TTL = settings.refresh_token_exp_days * 24 * 3600


def _key_refresh_token(token: str) -> str:
    return f"refresh:{token}"


def _key_user_refresh(user_id: int) -> str:
    return f"user:{user_id}:refresh"


async def cache_refresh_token(user_id: int, token: str):
    """Сохраняет refresh-токен в Redis с TTL и двухсторонним мэппингом."""
    redis = await get_redis()
    await redis.setex(_key_refresh_token(token), REFRESH_TTL, str(user_id))
    await redis.setex(_key_user_refresh(user_id), REFRESH_TTL, token)


async def get_user_id_by_refresh(token: str) -> int | None:
    """Получить user_id по refresh-токену."""
    redis = await get_redis()
    val = await redis.get(_key_refresh_token(token))
    return int(val) if val is not None else None


async def get_refresh_by_user(user_id: int) -> str | None:
    """Получить refresh-токен пользователя (последний сохранённый)."""
    redis = await get_redis()
    return await redis.get(_key_user_refresh(user_id))


async def revoke_refresh_token(token: str):
    """Отозвать конкретный refresh-токен."""
    redis = await get_redis()
    user_id = await redis.get(_key_refresh_token(token))
    await redis.delete(_key_refresh_token(token))
    if user_id:

        current = await redis.get(_key_user_refresh(int(user_id)))
        if current == token:
            await redis.delete(_key_user_refresh(int(user_id)))


async def revoke_user_refresh(user_id: int):
    """Отозвать refresh-токен по user_id."""
    redis = await get_redis()
    token = await redis.get(_key_user_refresh(user_id))
    await redis.delete(_key_user_refresh(user_id))
    if token:
        await redis.delete(_key_refresh_token(token))
