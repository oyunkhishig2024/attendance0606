"""The pivotal geofence check-in loop (spec §3.3). The client's own distance
computation is presentational only -- this is the authoritative, server-side
recomputation, and it is the single highest-value piece of this codebase."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from app import repo
from app.models import CheckInRequest
from app.services import schedule as schedule_service
from app.services.dates import iso_weekday, org_local_date_str
from app.services.fingerprint import hash_fingerprint
from app.services.geo import haversine_distance_m

STALE_CAPTURE_SECONDS = 5 * 60


@dataclass
class CheckInOutcome:
    ok: bool
    code: Optional[str] = None
    message: Optional[str] = None
    distance_m: Optional[float] = None
    record: Optional[dict] = None
    accuracy_required_retry: bool = False


def _parse_hhmm(value: str) -> tuple[int, int]:
    hour, minute = value.split(":")
    return int(hour), int(minute)


async def perform_checkin(organization_id: str, employee: dict, location: dict,
                           req: CheckInRequest, server_now: datetime) -> CheckInOutcome:
    if abs((server_now - req.captured_at).total_seconds()) > STALE_CAPTURE_SECONDS:
        return CheckInOutcome(ok=False, code="stale_capture",
                               message="Байршил хуучирсан байна, дахин оролдоно уу.")

    org = await repo.get_organization(organization_id)
    tz = ZoneInfo(org["timezone"])
    today_local = server_now.astimezone(tz)
    date_str = org_local_date_str(server_now, org["timezone"])

    existing = await repo.get_attendance_for_day(organization_id, employee["id"], date_str)
    if existing is not None:
        return CheckInOutcome(ok=True, record=existing, distance_m=existing.get("distance_m"))

    max_accuracy_m = location.get("max_accuracy_m", 100.0)
    if req.accuracy_m is not None and req.accuracy_m > max_accuracy_m:
        return CheckInOutcome(ok=False, code="accuracy_too_low", accuracy_required_retry=True,
                               message=f"Байршлын нарийвчлал хангалтгүй байна ({req.accuracy_m:.0f} м).")

    distance = haversine_distance_m(req.latitude, req.longitude, location["latitude"], location["longitude"])
    if distance > location["radius_m"]:
        return CheckInOutcome(
            ok=False, code="outside_geofence", distance_m=distance,
            message=f"Та салбараас {distance:.0f} м зайд байна (зөвшөөрөгдөх радиус {location['radius_m']:.0f} м).",
        )

    resolved_schedule = await schedule_service.resolve_schedule(organization_id, employee)
    work_days = schedule_service.effective_work_days(employee, resolved_schedule) if resolved_schedule else []
    holiday = await repo.is_holiday(organization_id, date_str)

    if holiday or iso_weekday(today_local) not in work_days:
        status = "off"
    else:
        hour, minute = _parse_hhmm(resolved_schedule["start_time"])
        shift_start = today_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        grace = timedelta(minutes=resolved_schedule.get("grace_minutes", 0))
        status = "on_time" if today_local <= shift_start + grace else "late"

    fingerprint_hash = hash_fingerprint(req.device_fingerprint)
    device_mismatch = bool(employee.get("registered_device")) and employee["registered_device"] != fingerprint_hash
    flagged = device_mismatch or req.mock_location_flag

    record = await repo.create_attendance(organization_id, {
        "employee_id": employee["id"],
        "location_id": location["id"],
        "date": date_str,
        "status": status,
        "check_in_time": server_now,
        "distance_m": distance,
        "accuracy_m": req.accuracy_m,
        "device_match": not device_mismatch,
        "mock_location_flag": req.mock_location_flag,
        "flagged": flagged,
    })
    return CheckInOutcome(ok=True, record=record, distance_m=distance)
