import pytest
import pytest_asyncio
from httpx import AsyncClient
from faker import Faker
from functional.settings import test_settings

fake = Faker()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
            base_url=f"http://{test_settings.auth_service_host}:{test_settings.auth_service_port}"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    email = fake.email()
    login = fake.user_name()
    password = "password123"

    resp = await async_client.post("/auth/register", json={"email": email, "login": login, "password": password})
    assert resp.status_code == 201
    assert resp.json()["login"] == login

    resp = await async_client.post("/auth/login", json={"login": login, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return login, password, data["access_token"], data["refresh_token"]


@pytest.mark.asyncio
async def test_refresh(async_client: AsyncClient):
    email = fake.email()
    login = fake.user_name()
    password = "password123"

    await async_client.post("/auth/register", json={"email": email, "login": login, "password": password})
    resp = await async_client.post("/auth/login", json={"login": login, "password": password})
    refresh_token = resp.json()["refresh_token"]

    resp = await async_client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_update_profile(async_client: AsyncClient):
    email = fake.email()
    login = fake.user_name()
    password = "password123"

    await async_client.post("/auth/register", json={"email": email, "login": login, "password": password})
    resp = await async_client.post("/auth/login", json={"login": login, "password": password})
    access_token = resp.json()["access_token"]

    new_login = fake.user_name()
    resp = await async_client.put(
        "/auth/profile",
        params={"authorization": f"Bearer {access_token}"},
        json={"login": new_login, "password": "newpass"},
    )
    assert resp.status_code == 200
    assert resp.json()["login"] == new_login


@pytest.mark.asyncio
async def test_get_history(async_client: AsyncClient):
    email = fake.email()
    login = fake.user_name()
    password = "password123"

    await async_client.post("/auth/register", json={"email": email, "login": login, "password": password})
    resp = await async_client.post("/auth/login", json={"login": login, "password": password})
    access_token = resp.json()["access_token"]

    resp = await async_client.get("/auth/history", params={"authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    email = fake.email()
    login = fake.user_name()
    password = "password123"

    await async_client.post("/auth/register", json={"email": email, "login": login, "password": password})
    resp = await async_client.post("/auth/login", json={"login": login, "password": password})
    refresh_token = resp.json()["refresh_token"]

    resp = await async_client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert resp.json() == {"detail": "Logged out"}
