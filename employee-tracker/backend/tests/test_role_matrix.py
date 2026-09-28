"""Role matrix test (spec §7.5): parameterised over (role x route), asserting
the expected status from §2.2 -- including the negative cases called out
explicitly: Manager on every POST, HR on tenant-user writes, and tenant
roles on /platform/*."""
import pytest

from app import repo
from app.security import hash_password
from tests.conftest import auth_headers, create_location, signup_org


async def _login_as(client, email: str, password: str = "password1") -> str:
    r = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["token"]


async def _seed_roles(client):
    admin_token, _, org = await signup_org(client, admin_email="admin@matrix.mn")
    admin_headers = auth_headers(admin_token)

    await client.post("/api/users", json={
        "name": "HR", "email": "hr@matrix.mn", "password": "password1", "role": "HR",
    }, headers=admin_headers)
    await client.post("/api/users", json={
        "name": "Manager", "email": "manager@matrix.mn", "password": "password1", "role": "Manager",
    }, headers=admin_headers)
    hr_token = await _login_as(client, "hr@matrix.mn")
    manager_token = await _login_as(client, "manager@matrix.mn")

    # Admin-created accounts start with must_change_password=True (spec §2.4),
    # which blocks every route but /auth/me and /auth/change-password. Clear
    # it so the role-matrix checks below exercise role gating, not this gate.
    for token in (hr_token, manager_token):
        r = await client.post("/api/auth/change-password", json={
            "current_password": "password1", "new_password": "password2",
        }, headers=auth_headers(token))
        assert r.status_code == 200, r.text

    location = await create_location(client, admin_token)

    return {"Admin": admin_token, "HR": hr_token, "Manager": manager_token, "org": org, "location": location}


@pytest.mark.asyncio
async def test_manager_is_read_only_everywhere(client):
    tokens = await _seed_roles(client)
    manager_headers = auth_headers(tokens["Manager"])

    write_attempts = [
        ("POST", "/api/locations", {"name": "X", "latitude": 0, "longitude": 0, "radius_m": 10, "start_time": "08:00"}),
        ("POST", "/api/employees", {"full_name": "X", "location_id": tokens["location"]["id"]}),
        ("POST", "/api/shifts", {"name": "X", "start_time": "08:00", "end_time": "17:00"}),
        ("POST", "/api/holidays", {"date": "2026-01-01", "name": "X"}),
        ("POST", "/api/users", {"name": "X", "email": "new@matrix.mn", "password": "password1", "role": "HR"}),
    ]
    for method, path, body in write_attempts:
        r = await client.request(method, path, json=body, headers=manager_headers)
        assert r.status_code == 403, f"Manager {method} {path} -> {r.status_code}: {r.text}"

    # Manager reads are allowed.
    for path in ("/api/locations", "/api/employees", "/api/shifts", "/api/holidays", "/api/users"):
        r = await client.get(path, headers=manager_headers)
        assert r.status_code == 200, f"Manager GET {path} -> {r.status_code}"


@pytest.mark.asyncio
async def test_hr_cannot_write_tenant_users_or_org_default_schedule(client):
    tokens = await _seed_roles(client)
    hr_headers = auth_headers(tokens["HR"])

    r = await client.post("/api/users", json={
        "name": "X", "email": "x@matrix.mn", "password": "password1", "role": "Manager",
    }, headers=hr_headers)
    assert r.status_code == 403

    r = await client.get("/api/shifts", headers=auth_headers(tokens["Admin"]))
    default_shift = next(s for s in r.json()["items"] if s["is_default"])
    r = await client.put(f"/api/shifts/{default_shift['id']}", json={"grace_minutes": 99}, headers=hr_headers)
    assert r.status_code == 403

    # HR *can* write employees, locations (read), shifts (non-default), holidays.
    r = await client.post("/api/employees", json={
        "full_name": "HR-created", "location_id": tokens["location"]["id"],
    }, headers=hr_headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_tenant_roles_get_403_on_platform_routes(client):
    tokens = await _seed_roles(client)
    for role in ("Admin", "HR", "Manager"):
        r = await client.get("/api/platform/organizations", headers=auth_headers(tokens[role]))
        assert r.status_code == 403, f"{role} -> {r.status_code}"


@pytest.mark.asyncio
async def test_system_admin_403_on_tenant_data_endpoints(client):
    await repo.create_user(organization_id=None, name="Platform", email="p@matrix.mn",
                            password_hash=hash_password("password1"), role="SystemAdmin")
    token = await _login_as(client, "p@matrix.mn")
    headers = auth_headers(token)
    for path in ("/api/employees", "/api/locations", "/api/shifts", "/api/holidays", "/api/users"):
        r = await client.get(path, headers=headers)
        assert r.status_code == 403, f"SystemAdmin GET {path} -> {r.status_code}"
