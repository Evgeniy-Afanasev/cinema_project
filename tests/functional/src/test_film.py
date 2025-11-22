import pytest
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio

async def test_film_not_found(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/123"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.NOT_FOUND


async def test_get_film_by_id(http_session: ClientSession, es_ready):
    # Arrange
    film_id = "ec1a0b58-0814-4369-ac44-cbefa03f8f96"

    # Act
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/{film_id}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert data["uuid"] == film_id


async def test_get_all_films_page_1(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/?page_number=1&page_size=3"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert len(data) == 3

    if data:
        assert "title" in data[0]
        assert "uuid" in data[0]


async def test_get_all_films_page_2(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/?page_number=2&page_size=3"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert len(data) == 3

    if data:
        assert "title" in data[0]
        assert "uuid" in data[0]


async def test_get_all_films_last_page(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/?page_number=4&page_size=3"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert len(data) == 1

    if data:
        assert "title" in data[0]
        assert "uuid" in data[0]


async def test_film_cache(http_session: ClientSession, redis_client, es_ready):
    # Arrange
    film_id = "ec1a0b58-0814-4369-ac44-cbefa03f8f96"
    await redis_client.flushdb()

    # Act 1
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/{film_id}"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK
    keys = await redis_client.keys("*")
    assert len(keys) > 0

    # Act 2
    async with http_session.get(
            f"http://{test_settings.movies_api_service_host}:{test_settings.movies_api_service_port}/api/v1/films/{film_id}"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2
