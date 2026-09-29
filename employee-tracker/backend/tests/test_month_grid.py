"""employee_month_grid (spec §4.5): off days must be explained (holiday vs
rest day) rather than appearing as gaps, and a past workday with no record
reads as `absent` rather than nothing -- but a future/today workday with no
record yet must NOT be prematurely marked absent."""
from datetime import date

import pytest

from app import repo
from app.services.month_grid import build_employee_month_grid

PAST_MONTH = "2020-01"   # every day in this month is in the past, deterministically
FUTURE_MONTH = "2099-01"  # every day in this month is in the future, deterministically


async def _setup():
    org = await repo.create_organization("Grid Org")
    await repo.create_default_schedule(org["id"])  # Mon-Fri, work_days [1..5]
    location = await repo.create_location(org["id"], {
        "name": "Branch", "latitude": 0, "longitude": 0, "radius_m": 100, "start_time": "08:30",
    })
    employee = await repo.create_employee(org["id"], {"full_name": "Grid Employee", "location_id": location["id"]})
    return org, location, employee


def _find(grid, date_str):
    return next(d for d in grid if d["date"] == date_str)


@pytest.mark.asyncio
async def test_past_workday_with_no_record_is_absent():
    org, location, employee = await _setup()
    grid = await build_employee_month_grid(org["id"], employee, PAST_MONTH)
    workday = next(
        d for d in grid if date.fromisoformat(d["date"]).isoweekday() in (1, 2, 3, 4, 5)
    )
    assert workday["status"] == "absent"
    assert workday["explanation"] is None


@pytest.mark.asyncio
async def test_weekend_with_no_record_is_off_rest_day():
    org, location, employee = await _setup()
    grid = await build_employee_month_grid(org["id"], employee, PAST_MONTH)
    weekend = next(d for d in grid if date.fromisoformat(d["date"]).isoweekday() in (6, 7))
    assert weekend["status"] == "off"
    assert weekend["explanation"] == "rest_day"


@pytest.mark.asyncio
async def test_holiday_on_a_workday_is_off_holiday_not_absent():
    org, location, employee = await _setup()
    workday_dates = [d for d in _month_dates(PAST_MONTH) if date.fromisoformat(d).isoweekday() in (1, 2, 3, 4, 5)]
    holiday_date = workday_dates[0]
    await repo.create_holiday(org["id"], holiday_date, "Test Holiday")

    grid = await build_employee_month_grid(org["id"], employee, PAST_MONTH)
    day = _find(grid, holiday_date)
    assert day["status"] == "off"
    assert day["explanation"] == "holiday"


@pytest.mark.asyncio
async def test_future_workday_with_no_record_is_pending_not_absent():
    org, location, employee = await _setup()
    grid = await build_employee_month_grid(org["id"], employee, FUTURE_MONTH)
    workday = next(
        d for d in grid if date.fromisoformat(d["date"]).isoweekday() in (1, 2, 3, 4, 5)
    )
    assert workday["status"] is None
    assert workday["explanation"] == "pending"


@pytest.mark.asyncio
async def test_actual_attendance_record_is_reflected_verbatim():
    org, location, employee = await _setup()
    workday_dates = [d for d in _month_dates(PAST_MONTH) if date.fromisoformat(d).isoweekday() in (1, 2, 3, 4, 5)]
    checked_in_date = workday_dates[1]
    await repo.create_attendance(org["id"], {
        "employee_id": employee["id"], "location_id": location["id"], "date": checked_in_date,
        "status": "late", "check_in_time": None, "distance_m": 42.0, "accuracy_m": 10.0,
        "device_match": True, "mock_location_flag": False, "flagged": False,
    })

    grid = await build_employee_month_grid(org["id"], employee, PAST_MONTH)
    day = _find(grid, checked_in_date)
    assert day["status"] == "late"
    assert day["distance_m"] == 42.0
    assert day["explanation"] is None


def _month_dates(month: str) -> list[str]:
    from app.services.dates import days_in_month
    return days_in_month(month)
