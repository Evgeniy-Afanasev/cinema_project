import pytest
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import test_settings


@pytest.mark.asyncio
async def test_healthcheck(http_session: ClientSession):
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/health"
    ) as resp:
        data = await resp.json()

    assert resp.status == HTTPStatus.OK
    assert data == {"status": "healthy"}
