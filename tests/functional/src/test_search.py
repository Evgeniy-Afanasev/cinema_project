import pytest
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import test_settings


@pytest.mark.asyncio
async def test_search_validation_page_size(http_session: ClientSession):
    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?page_size=-1"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search_validation_page_number(http_session: ClientSession):
    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?page_number=-1"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search_validation_sort(http_session: ClientSession):
    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?sort=-1"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search_limit_records(http_session: ClientSession, es_ready):
    # Arrange
    phrase = "Include"
    N = 2

    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?query={phrase}&page_size={N}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert len(data) <= N


@pytest.mark.asyncio
async def test_search_by_phrase(http_session: ClientSession, es_ready):
    # Arrange
    phrase = "Include"

    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?query={phrase}&page=1&size=5"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert any(phrase.lower() in f["title"].lower() for f in data)


@pytest.mark.asyncio
async def test_search_with_sorting_ascending(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?sort=imdb_rating&page=1&size=10"
    ) as resp:
        data_sorted = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert [f["imdb_rating"] for f in data_sorted] == sorted([f["imdb_rating"] for f in data_sorted])


@pytest.mark.asyncio
async def test_search_with_sorting_descending(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?sort=-imdb_rating&page=1&size=10"
    ) as resp:
        data_sorted_reverse = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert [f["imdb_rating"] for f in data_sorted_reverse] == sorted([f["imdb_rating"] for f in data_sorted_reverse],
                                                                     reverse=True)


@pytest.mark.asyncio
async def test_search_cache(http_session: ClientSession, redis_client, es_ready):
    # Arrange
    phrase = "Include"
    await redis_client.flushdb()

    # Act 1
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?query={phrase}&page_number=1&page_size=3"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK

    # Act 2
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?query={phrase}&page_number=1&page_size=3"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2


@pytest.mark.asyncio
async def test_search_pagination(http_session: ClientSession, es_ready):
    # Arrange

    # Act 1 - First page
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?page_number=1&page_size=3"
    ) as resp1:
        data1 = await resp1.json()

    # Act 2 - Second page
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?page_number=2&page_size=3"
    ) as resp2:
        data2 = await resp2.json()

    # Act 3 - Third page
    async with http_session.get(
            f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films/search?page_number=3&page_size=3"
    ) as resp3:
        data3 = await resp3.json()

    # Assert 1 - First page results
    assert resp1.status == HTTPStatus.OK
    assert len(data1) == 3

    # Assert 2 - Second page results
    assert resp2.status == HTTPStatus.OK
    assert len(data2) == 3

    # Assert 3 - Third page results
    assert resp3.status == HTTPStatus.OK
    assert len(data3) == 3

    assert data1 != data2
    assert data2 != data3
