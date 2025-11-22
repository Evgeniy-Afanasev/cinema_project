import backoff
import asyncio
import asyncpg
from functional.settings import test_settings


@backoff.on_exception(backoff.expo, (asyncpg.exceptions.PostgresError, Exception), max_time=60)
async def ping_postgres():
    conn = await asyncpg.connect(
        host=test_settings.postgres_host,
        port=test_settings.postgres_port,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        database=test_settings.postgres_auth_db
    )
    await conn.close()


if __name__ == '__main__':
    try:
        asyncio.run(ping_postgres())
        print("PostgreSQL is reachable.")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
