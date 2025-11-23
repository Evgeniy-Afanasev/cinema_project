import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import User, LoginHistory
from utils.security import hash_password, verify_password
from utils.jwt import create_access_token
from utils.token_cache import cache_refresh_token, get_user_id_by_refresh, revoke_refresh_token
from core.config import settings


class AuthService:
    """Авторизация: регистрация, вход, refresh, logout, профиль, история входов."""

    async def register(self, db: AsyncSession, email: str, login: str, password: str) -> User:
        exists = await db.execute(select(User).where((User.email == email) | (User.login == login)))
        if exists.unique().scalars().first():
            raise ValueError("Email или login уже заняты")
        user = User(email=email, login=login, password_hash=hash_password(password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def login(self, db: AsyncSession, login: str, password: str, ip: str | None, ua: str | None):
        res = await db.execute(select(User).where(User.login == login))
        user = res.unique().scalars().first()
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Неверные учетные данные")

        access = create_access_token(user)
        refresh_value = str(uuid.uuid4())

        await cache_refresh_token(user.id, refresh_value)

        db.add(LoginHistory(user_id=user.id, ip_address=ip, user_agent=ua))
        await db.commit()

        return access, refresh_value, settings.access_token_exp_minutes * 60

    async def refresh(self, db: AsyncSession, refresh_token: str):
        user_id = await get_user_id_by_refresh(refresh_token)
        if not user_id:
            raise ValueError("Недействительный refresh-токен")

        res = await db.execute(select(User).where(User.id == user_id))
        user = res.unique().scalars().first()
        if not user or not user.is_active:
            raise ValueError("Пользователь недоступен")

        access = create_access_token(user)
        return access, refresh_token, settings.access_token_exp_minutes * 60

    async def logout(self, db: AsyncSession, refresh_token: str):
        await revoke_refresh_token(refresh_token)

    async def update_profile(self, db: AsyncSession, user_id: int, login: str | None, password: str | None) -> User:
        res = await db.execute(select(User).where(User.id == user_id))
        user = res.unique().scalars().first()
        if not user:
            raise ValueError("Пользователь не найден")

        if login:
            exists = await db.execute(select(User).where((User.login == login) & (User.id != user_id)))
            if exists.unique().scalars().first():
                raise ValueError("Логин уже занят")
            user.login = login
        if password:
            user.password_hash = hash_password(password)

        await db.commit()
        await db.refresh(user)
        return user

    async def history(self, db: AsyncSession, user_id: int):
        res = await db.execute(
            select(LoginHistory).where(LoginHistory.user_id == user_id).order_by(LoginHistory.created_at.desc())
        )
        return list(res.scalars().all())
