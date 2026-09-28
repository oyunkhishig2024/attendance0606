import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db import ensure_indexes, reset_db_for_tests
from app.main import app
from app.services.ratelimit import reset_for_tests as reset_rate_limits


@pytest_asyncio.fixture
async def client():
    reset_db_for_tests()
    reset_rate_limits()
    await ensure_indexes()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def signup_org(client, *, org_name="Org", admin_email="admin@org.mn", password="password1"):
    r = await client.post("/api/auth/signup", json={
        "organization_name": org_name, "admin_name": "Admin", "email": admin_email, "password": password,
    })
    assert r.status_code == 200, r.text
    body = r.json()
    return body["token"], body["user"], body["organization"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def create_location(client, token, **overrides):
    payload = {
        "name": "Branch", "latitude": 47.9188, "longitude": 106.9176, "radius_m": 150,
        "start_time": "08:30", "grace_minutes": 10, "max_accuracy_m": 100,
    }
    payload.update(overrides)
    r = await client.post("/api/locations", json=payload, headers=auth_headers(token))
    assert r.status_code == 200, r.text
    return r.json()


async def create_employee(client, token, location_id, **overrides):
    payload = {"full_name": "Employee", "department": "Sales", "location_id": location_id}
    payload.update(overrides)
    r = await client.post("/api/employees", json=payload, headers=auth_headers(token))
    assert r.status_code == 200, r.text
    return r.json()
