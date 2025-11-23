from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Role, User
from schemas.auth import RoleCreate


class RoleService:
    """Сервис управления ролями: CRUD, назначение/отбор, проверка прав."""

    async def create_role(self, db: AsyncSession, payload: RoleCreate) -> Role:
        exists = await db.execute(select(Role).where(Role.name == payload.name))
        if exists.scalars().first():
            raise ValueError("Роль уже существует")
        role = Role(name=payload.name)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    async def list_roles(self, db: AsyncSession) -> list[Role]:
        res = await db.execute(select(Role).order_by(Role.name.asc()))
        return list(res.unique().scalars().all())

    async def update_role(self, db: AsyncSession, role_id: int, payload: RoleCreate) -> Role:
        res = await db.execute(select(Role).where(Role.id == role_id))
        role = res.scalars().first()
        if not role:
            raise ValueError("Роль не найдена")
        if role.name != payload.name:
            exists = await db.execute(select(Role).where(Role.name == payload.name))
            if exists.scalars().first():
                raise ValueError("Имя роли уже занято")
        role.name = payload.name
        await db.commit()
        await db.refresh(role)
        return role

    async def delete_role(self, db: AsyncSession, role_id: int) -> None:
        res = await db.execute(select(Role).where(Role.id == role_id))
        role = res.scalars().first()
        if not role:
            raise ValueError("Роль не найдена")
        await db.delete(role)
        await db.commit()

    async def assign_role(self, db: AsyncSession, login: str, role_name: str) -> None:
        ures = await db.execute(select(User).where(User.login == login))
        user = ures.scalars().first()
        if not user:
            raise ValueError("Пользователь не найден")
        rres = await db.execute(select(Role).where(Role.name == role_name))
        role = rres.scalars().first()
        if not role:
            raise ValueError("Роль не найдена")
        if role in user.roles:
            return
        user.roles.append(role)
        await db.commit()

    async def revoke_role(self, db: AsyncSession, login: str, role_name: str) -> None:
        ures = await db.execute(select(User).where(User.login == login))
        user = ures.scalars().first()
        if not user:
            raise ValueError("Пользователь не найден")
        rres = await db.execute(select(Role).where(Role.name == role_name))
        role = rres.scalars().first()
        if not role:
            raise ValueError("Роль не найдена")
        if role in user.roles:
            user.roles.remove(role)
            await db.commit()

    async def check_access(self, db: AsyncSession, login: str, required_role: str) -> bool:
        ures = await db.execute(select(User).where(User.login == login))
        user = ures.scalars().first()
        if not user:
            raise ValueError("Пользователь не найден")
        return any(r.name == required_role for r in user.roles)
