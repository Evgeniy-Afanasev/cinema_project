import datetime
import hashlib
import os
import typer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.models import User
from core.config import settings
from alembic.config import Config
from alembic import command

dsn = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
engine = create_engine(dsn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = typer.Typer()


def run_migrations():
    """Запуск alembic upgrade head из скрипта."""
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@app.command()
def create_superuser(
        email: str = typer.Option(..., "--email", help="Email пользователя"),
        login: str = typer.Option(..., "--login", help="Логин пользователя"),
        password: str = typer.Option(..., "--password", help="Пароль пользователя"),
):
    """Создание суперпользователя с автоматическим применением миграций."""

    run_migrations()

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter((User.email == email) | (User.login == login)).first()
        if existing_user:
            typer.echo("Пользователь с таким email или логином уже существует.")
            return

        new_user = User(
            email=email,
            login=login,
            password_hash=hash_password(password),
            is_active=True,
            is_superuser=True,
            created_at=datetime.datetime.utcnow(),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        typer.echo(f"Суперпользователь {new_user.login} успешно создан.")
    except Exception as e:
        db.rollback()
        typer.echo(f"Произошла ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()
