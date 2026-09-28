"""Highest-value unit tests per spec §7.2: status resolution boundary
behaviour, schedule precedence, and holiday/non-working-day handling --
exercised directly against the service so server_now can be controlled
precisely, independent of wall-clock time."""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app import repo
from app.models import CheckInRequest
from app.services.checkin import perform_checkin
from app.services.schedule import resolve_schedule

TZ = ZoneInfo("Asia/Ulaanbaatar")
MONDAY = "2026-09-28"
SATURDAY = "2026-10-03"


def local(date_str: str, hour: int, minute: int) -> datetime:
    y, m, d = map(int, date_str.split("-"))
    return datetime(y, m, d, hour, minute, tzinfo=TZ)


async def _setup_org_with_location_and_employee(**employee_overrides):
    org = await repo.create_organization("Test Org")
    schedule = await repo.create_default_schedule(org["id"])
    location = await repo.create_location(org["id"], {
        "name": "Branch", "latitude": 47.9188, "longitude": 106.9176, "radius_m": 150,
        "start_time": "08:30", "grace_minutes": 10, "max_accuracy_m": 100,
    })
    employee = await repo.create_employee(org["id"], {
        "full_name": "Test Employee", "department": None, "location_id": location["id"],
        "shift_template_id": None, **employee_overrides,
    })
    return org, schedule, location, employee


def _req(server_now: datetime, **overrides) -> CheckInRequest:
    payload = dict(latitude=47.9188, longitude=106.9176, accuracy_m=10.0,
                    captured_at=server_now, device_fingerprint="device-a", mock_location_flag=False)
    payload.update(overrides)
    return CheckInRequest(**payload)


@pytest.mark.parametrize("hour,minute,expected", [
    (8, 30, "on_time"),   # exactly at shift start
    (8, 40, "on_time"),   # exactly at shift_start + grace_minutes (10)
    (8, 41, "late"),      # one minute past grace
    (7, 0, "on_time"),    # arriving early is never late
])
async def test_status_boundary_at_grace_window(hour, minute, expected):
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(MONDAY, hour, minute)
    outcome = await perform_checkin(org["id"], employee, location, _req(server_now), server_now)
    assert outcome.ok
    assert outcome.record["status"] == expected


async def test_off_on_non_working_day():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(SATURDAY, 9, 0)
    outcome = await perform_checkin(org["id"], employee, location, _req(server_now), server_now)
    assert outcome.ok
    assert outcome.record["status"] == "off"


async def test_off_on_holiday_even_if_normally_a_workday():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    await repo.create_holiday(org["id"], MONDAY, "Test Holiday")
    server_now = local(MONDAY, 9, 0)
    outcome = await perform_checkin(org["id"], employee, location, _req(server_now), server_now)
    assert outcome.ok
    assert outcome.record["status"] == "off"


async def test_outside_geofence_is_rejected_with_distance():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(MONDAY, 8, 30)
    far_req = _req(server_now, latitude=47.0, longitude=106.0)
    outcome = await perform_checkin(org["id"], employee, location, far_req, server_now)
    assert not outcome.ok
    assert outcome.code == "outside_geofence"
    assert outcome.distance_m > location["radius_m"]


async def test_boundary_at_exact_radius_passes_one_cm_beyond_fails():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(MONDAY, 8, 30)

    # Move latitude so distance is just inside vs. just outside a tight radius.
    tight_location = dict(location)
    tight_location["radius_m"] = 100

    just_inside = _req(server_now, latitude=47.9188 + 0.00089, longitude=106.9176)  # ~99m
    outcome_inside = await perform_checkin(org["id"], employee, tight_location, just_inside, server_now)
    assert outcome_inside.ok

    employee2 = await repo.create_employee(org["id"], {
        "full_name": "Employee 2", "location_id": location["id"], "shift_template_id": None,
    })
    just_outside = _req(server_now, latitude=47.9188 + 0.00095, longitude=106.9176)  # ~105m
    outcome_outside = await perform_checkin(org["id"], employee2, tight_location, just_outside, server_now)
    assert not outcome_outside.ok
    assert outcome_outside.code == "outside_geofence"


async def test_idempotent_replay_returns_existing_record():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(MONDAY, 8, 30)
    first = await perform_checkin(org["id"], employee, location, _req(server_now), server_now)
    second = await perform_checkin(org["id"], employee, location, _req(server_now), server_now)
    assert first.record["id"] == second.record["id"]


async def test_stale_capture_rejected():
    org, schedule, location, employee = await _setup_org_with_location_and_employee()
    server_now = local(MONDAY, 8, 30)
    stale_req = _req(server_now.replace(minute=0))
    outcome = await perform_checkin(org["id"], employee, location, stale_req, server_now)
    assert not outcome.ok
    assert outcome.code == "stale_capture"


async def test_device_mismatch_flags_but_does_not_block():
    org, schedule, location, employee = await _setup_org_with_location_and_employee(
        registered_device="hash-of-device-a",
    )
    server_now = local(MONDAY, 8, 30)
    req = _req(server_now, device_fingerprint="device-b")
    outcome = await perform_checkin(org["id"], employee, location, req, server_now)
    assert outcome.ok
    assert outcome.record["flagged"] is True
    assert outcome.record["device_match"] is False


# ---- schedule precedence (spec §3.4 / §7.2 item 4) --------------------------

async def test_schedule_precedence_employee_beats_department_beats_location_beats_default():
    org = await repo.create_organization("Precedence Org")
    default_schedule = await repo.create_default_schedule(org["id"])
    plain_location = await repo.create_location(org["id"], {
        "name": "Plain Branch", "latitude": 0, "longitude": 0, "radius_m": 100, "start_time": "08:30",
    })
    scheduled_location = await repo.create_location(org["id"], {
        "name": "Scheduled Branch", "latitude": 0, "longitude": 0, "radius_m": 100, "start_time": "08:30",
    })

    dept_schedule = await repo.create_shift_template(org["id"], {
        "name": "Dept", "start_time": "09:00", "end_time": "18:00", "grace_minutes": 0,
        "work_days": [1, 2, 3, 4, 5], "assigned_departments": ["Eng"], "assigned_location_ids": [],
    })
    location_schedule = await repo.create_shift_template(org["id"], {
        "name": "Loc", "start_time": "10:00", "end_time": "19:00", "grace_minutes": 0,
        "work_days": [1, 2, 3, 4, 5], "assigned_departments": [], "assigned_location_ids": [scheduled_location["id"]],
    })
    employee_schedule = await repo.create_shift_template(org["id"], {
        "name": "Emp", "start_time": "11:00", "end_time": "20:00", "grace_minutes": 0,
        "work_days": [1, 2, 3, 4, 5], "assigned_departments": [], "assigned_location_ids": [],
    })

    # No department/location match anywhere -> org default.
    plain_employee = await repo.create_employee(org["id"], {
        "full_name": "Plain", "location_id": plain_location["id"], "department": "Other", "shift_template_id": None,
    })
    resolved = await resolve_schedule(org["id"], plain_employee)
    assert resolved["id"] == default_schedule["id"]

    # Location match beats default.
    location_employee = await repo.create_employee(org["id"], {
        "full_name": "LocEmp", "location_id": scheduled_location["id"], "department": "Other",
        "shift_template_id": None,
    })
    resolved = await resolve_schedule(org["id"], location_employee)
    assert resolved["id"] == location_schedule["id"]

    # Department match beats a location match that would otherwise apply.
    dept_employee = await repo.create_employee(org["id"], {
        "full_name": "DeptEmp", "location_id": scheduled_location["id"], "department": "Eng",
        "shift_template_id": None,
    })
    resolved = await resolve_schedule(org["id"], dept_employee)
    assert resolved["id"] == dept_schedule["id"]

    # Explicit employee assignment beats everything.
    emp_employee = await repo.create_employee(org["id"], {
        "full_name": "EmpEmp", "location_id": scheduled_location["id"], "department": "Eng",
        "shift_template_id": employee_schedule["id"],
    })
    resolved = await resolve_schedule(org["id"], emp_employee)
    assert resolved["id"] == employee_schedule["id"]


async def test_deactivating_schedule_falls_back_to_default_on_next_resolution():
    org = await repo.create_organization("Fallback Org")
    default_schedule = await repo.create_default_schedule(org["id"])
    location = await repo.create_location(org["id"], {
        "name": "Branch", "latitude": 0, "longitude": 0, "radius_m": 100, "start_time": "08:30",
    })
    custom = await repo.create_shift_template(org["id"], {
        "name": "Custom", "start_time": "09:00", "end_time": "18:00", "grace_minutes": 0,
        "work_days": [1, 2, 3, 4, 5],
    })
    employee = await repo.create_employee(org["id"], {
        "full_name": "Emp", "location_id": location["id"], "shift_template_id": custom["id"],
    })
    assert (await resolve_schedule(org["id"], employee))["id"] == custom["id"]

    await repo.update_shift_template(org["id"], custom["id"], {"is_active": False})
    resolved = await resolve_schedule(org["id"], employee)
    assert resolved["id"] == default_schedule["id"]
