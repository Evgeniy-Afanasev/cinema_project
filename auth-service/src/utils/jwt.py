import datetime
import uuid
import jwt
from core.config import settings
from models.models import User


def create_access_token(user: User) -> str:
    """Создаёт JWT access-токен с ролями пользователя."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user.id),
        "login": user.login,
        "roles": [r.name for r in user.roles],
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(minutes=settings.access_token_exp_minutes)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> dict:
    """Декодирует и валидирует JWT токен, возвращает payload."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
