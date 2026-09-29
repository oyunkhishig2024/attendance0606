"""Reason logging (spec §3.5): role gating, the 15-item preset catalogue,
multi-employee/date-range writes, and the rule that a reason log must never
clobber an existing check-in's time/distance -- only its status."""
from datetime import datetime, timezone

import pytest

from app import repo
from app.models import CheckInRequest
from app.services.checkin import perform_checkin
from tests.conftest import auth_headers, create_employee, create_location, signup_org


async def _seed(client):
    token, _, org = await signup_org(client, admin_email="reasons-admin@example.com")
    headers = auth_headers(token)
    location = await create_location(client, token)
    employee = await create_employee(client, token, location["id"])
    return {"token": token, "headers": headers, "org": org, "location": location, "employee": employee}


@pytest.mark.asyncio
async def test_catalog_has_fifteen_preset_reasons(client):
    ctx = await _seed(client)
    r = await client.get("/api/reasons/catalog", headers=ctx["headers"])
    assert r.status_code == 200
    assert len(r.json()["items"]) == 15


@pytest.mark.asyncio
async def test_manager_cannot_post_reasons(client):
    ctx = await _seed(client)
    await client.post("/api/users", json={
        "name": "Mgr", "email": "mgr@example.com", "password": "password1", "role": "Manager",
    }, headers=ctx["headers"])
    r = await client.post("/api/auth/login", json={"email": "mgr@example.com", "password": "password1"})
    manager_token = r.json()["token"]
    await client.post("/api/auth/change-password", json={
        "current_password": "password1", "new_password": "password2",
    }, headers=auth_headers(manager_token))

    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"]], "reason_key": "sick",
        "start_date": "2026-01-05", "end_date": "2026-01-05",
    }, headers=auth_headers(manager_token))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_invalid_reason_key_rejected(client):
    ctx = await _seed(client)
    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"]], "reason_key": "not_a_real_reason",
        "start_date": "2026-01-05", "end_date": "2026-01-05",
    }, headers=ctx["headers"])
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_reason_key"


@pytest.mark.asyncio
async def test_reason_log_creates_attendance_when_none_existed(client):
    ctx = await _seed(client)
    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"]], "reason_key": "sick",
        "start_date": "2026-01-05", "end_date": "2026-01-07", "note": "Flu",
    }, headers=ctx["headers"])
    assert r.status_code == 200, r.text
    assert len(r.json()["items"]) == 1  # one reason_logs row per employee, spanning the range

    r = await client.get(f"/api/attendance?date=2026-01-06", headers=ctx["headers"])
    records = r.json()["items"]
    assert len(records) == 1
    assert records[0]["status"] == "reason"
    assert records[0]["employee_id"] == ctx["employee"]["id"]


@pytest.mark.asyncio
async def test_reason_log_preserves_existing_check_in_time_and_distance(client):
    ctx = await _seed(client)
    server_now = datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc)  # a Monday, ~ noon in Ulaanbaatar
    req = CheckInRequest(
        latitude=ctx["location"]["latitude"], longitude=ctx["location"]["longitude"], accuracy_m=10.0,
        captured_at=server_now, device_fingerprint="device-a", mock_location_flag=False,
    )
    outcome = await perform_checkin(ctx["org"]["id"], ctx["employee"], ctx["location"], req, server_now)
    assert outcome.ok
    original_check_in_time = outcome.record["check_in_time"]
    original_distance = outcome.record["distance_m"]

    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"]], "reason_key": "medical_appointment",
        "start_date": "2026-01-05", "end_date": "2026-01-05",
    }, headers=ctx["headers"])
    assert r.status_code == 200, r.text

    updated = await repo.get_attendance_for_day(ctx["org"]["id"], ctx["employee"]["id"], "2026-01-05")
    assert updated["status"] == "reason"

    updated_check_in_time = updated["check_in_time"]
    if updated_check_in_time.tzinfo is None:
        updated_check_in_time = updated_check_in_time.replace(tzinfo=timezone.utc)
    assert updated_check_in_time == original_check_in_time
    assert updated["distance_m"] == original_distance


@pytest.mark.asyncio
async def test_invalid_employee_id_rejects_before_writing_any_rows(client):
    ctx = await _seed(client)
    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"], "not-a-real-employee-id"], "reason_key": "sick",
        "start_date": "2026-03-01", "end_date": "2026-03-01",
    }, headers=ctx["headers"])
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_employee"

    r = await client.get(f"/api/reasons?employee_id={ctx['employee']['id']}", headers=ctx["headers"])
    assert r.json()["items"] == []

    r = await client.get("/api/attendance?date=2026-03-01", headers=ctx["headers"])
    assert r.json()["items"] == []


@pytest.mark.asyncio
async def test_reason_log_multi_employee_writes_one_row_each(client):
    ctx = await _seed(client)
    employee2 = await create_employee(client, ctx["token"], ctx["location"]["id"], full_name="Second Employee")

    r = await client.post("/api/reasons", json={
        "employee_ids": [ctx["employee"]["id"], employee2["id"]], "reason_key": "annual_leave",
        "start_date": "2026-02-01", "end_date": "2026-02-03",
    }, headers=ctx["headers"])
    assert r.status_code == 200, r.text
    assert len(r.json()["items"]) == 2

    r = await client.get(f"/api/reasons?employee_id={employee2['id']}", headers=ctx["headers"])
    assert len(r.json()["items"]) == 1
    assert r.json()["items"][0]["reason_key"] == "annual_leave"
