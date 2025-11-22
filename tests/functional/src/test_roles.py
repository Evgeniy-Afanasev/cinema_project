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
async def test_create_and_list_roles(async_client: AsyncClient):
    role_name = fake.job()
    resp = await async_client.post("/roles/", json={"name": role_name})
    assert resp.status_code == 201
    assert resp.json()["name"] == role_name

    resp = await async_client.get("/roles/")
    assert resp.status_code == 200
    assert any(r["name"] == role_name for r in resp.json())


@pytest.mark.asyncio
async def test_assign_check_revoke_role(async_client: AsyncClient):
    login = fake.user_name()
    email = fake.email()
    await async_client.post("/auth/register", json={"email": email, "login": login, "password": "pass123"})

    role_name = fake.job()
    await async_client.post("/roles/", json={"name": role_name})

    resp = await async_client.post("/roles/assign", json={"login": login, "required_role": role_name})
    assert resp.status_code == 200

    resp = await async_client.post("/roles/check", json={"login": login, "required_role": role_name})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True

    resp = await async_client.post("/roles/revoke", json={"login": login, "required_role": role_name})
    assert resp.status_code == 200

    resp = await async_client.post("/roles/check", json={"login": login, "required_role": role_name})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False
