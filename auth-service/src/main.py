from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.postgres import engine, Base
from db.redis import init_redis
from routers import auth, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_redis()
    yield
    await engine.dispose()


app = FastAPI(
    title='auth',
    description='Сервис авторизации',
    docs_url='/docs',
    openapi_url='/openapi.json',
    lifespan=lifespan,
    root_path="/auth"
)

app.include_router(auth.router, prefix='/auth', tags=["auth"])
app.include_router(roles.router, prefix='/roles', tags=["roles"])
