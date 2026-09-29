"""The mandatory tenant-isolation gate (spec §7.4): must never be skipped or
quarantined. Seeds two organizations, authenticates as A, and asserts that
substituting B's ids into every authenticated, id-addressed route never
returns a document belonging to B -- only 403 or 404."""
import pytest

from tests.conftest import auth_headers, create_employee, create_location, signup_org


async def _seed_org(client, suffix: str):
    token, user, org = await signup_org(
        client, org_name=f"Org {suffix}", admin_email=f"admin-{suffix}@example.com",
    )
    headers = auth_headers(token)
    location = await create_location(client, token, name=f"Branch {suffix}")
    employee = await create_employee(client, token, location["id"], full_name=f"Employee {suffix}")

    r = await client.post("/api/shifts", json={
        "name": f"Shift {suffix}", "start_time": "09:00", "end_time": "18:00",
    }, headers=headers)
    shift = r.json()

    r = await client.post("/api/holidays", json={"date": "2026-01-01", "name": f"Holiday {suffix}"},
                           headers=headers)
    holiday = r.json()

    r = await client.post("/api/users", json={
        "name": f"HR {suffix}", "email": f"hr-{suffix}@example.com", "password": "password1", "role": "HR",
    }, headers=headers)
    hr_user = r.json()

    return {
        "token": token, "org": org, "location": location, "employee": employee,
        "shift": shift, "holiday": holiday, "hr_user": hr_user,
    }


@pytest.mark.asyncio
async def test_tenant_a_cannot_reach_tenant_b_documents(client):
    a = await _seed_org(client, "a")
    b = await _seed_org(client, "b")
    headers_a = auth_headers(a["token"])

    # Substitute B's ids into every id-addressed authenticated route, as A.
    attempts = [
        ("PUT", f"/api/users/{b['hr_user']['id']}"),
        ("DELETE", f"/api/users/{b['hr_user']['id']}"),
        ("PUT", f"/api/locations/{b['location']['id']}"),
        ("DELETE", f"/api/locations/{b['location']['id']}"),
        ("GET", f"/api/employees/{b['employee']['id']}"),
        ("PUT", f"/api/employees/{b['employee']['id']}"),
        ("DELETE", f"/api/employees/{b['employee']['id']}"),
        ("PUT", f"/api/shifts/{b['shift']['id']}"),
        ("PATCH", f"/api/shifts/{b['shift']['id']}/active?is_active=false"),
        ("DELETE", f"/api/shifts/{b['shift']['id']}"),
        ("DELETE", f"/api/holidays/{b['holiday']['id']}"),
    ]
    for method, path in attempts:
        r = await client.request(method, path, headers=headers_a, json={} if method in ("PUT",) else None)
        assert r.status_code in (403, 404), f"{method} {path} -> {r.status_code}: {r.text}"
        if r.status_code == 200:
            assert b["org"]["id"] not in r.text

    # List endpoints must never contain any of B's ids either.
    b_ids = {b["employee"]["id"], b["location"]["id"], b["shift"]["id"], b["holiday"]["id"], b["hr_user"]["id"]}
    for path in ("/api/users", "/api/locations", "/api/employees", "/api/shifts", "/api/holidays"):
        r = await client.get(path, headers=headers_a)
        assert r.status_code == 200
        for leaked_id in b_ids:
            assert leaked_id not in r.text, f"{path} leaked tenant B id {leaked_id}"

    # GET on B's employee by id (a read, not just a write) must not leak either.
    r = await client.get(f"/api/employees/{b['employee']['id']}", headers=headers_a)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_platform_admin_gets_403_on_every_tenant_route(client):
    import os

    from app import repo
    from app.security import hash_password

    a = await _seed_org(client, "c")
    await repo.create_user(organization_id=None, name="Platform", email="platform@example.com",
                            password_hash=hash_password("password1"), role="SystemAdmin")
    r = await client.post("/api/auth/login", json={"email": "platform@example.com", "password": "password1"})
    platform_token = r.json()["token"]
    headers = auth_headers(platform_token)

    for path in ("/api/users", "/api/locations", "/api/employees", "/api/shifts", "/api/holidays",
                 "/api/attendance?date=2026-01-01"):
        r = await client.get(path, headers=headers)
        assert r.status_code == 403, f"GET {path} -> {r.status_code}"


@pytest.mark.asyncio
async def test_tenant_admin_gets_403_on_every_platform_route(client):
    a = await _seed_org(client, "d")
    headers = auth_headers(a["token"])

    for method, path in [
        ("GET", "/api/platform/organizations"),
        ("POST", "/api/platform/organizations"),
        ("PATCH", "/api/platform/organizations/some-id/suspend"),
        ("PATCH", "/api/platform/organizations/some-id/reactivate"),
        ("GET", "/api/platform/analytics"),
        ("GET", "/api/platform/audit-logs"),
    ]:
        r = await client.request(method, path, headers=headers, json={} if method == "POST" else None)
        assert r.status_code == 403, f"{method} {path} -> {r.status_code}"
