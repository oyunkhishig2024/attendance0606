from fastapi import APIRouter, Depends

from app import repo
from app.deps import CurrentUser, require_tenant_read

router = APIRouter(prefix="/api", tags=["attendance"])


@router.get("/attendance")
async def list_attendance(date: str | None = None, location_id: str | None = None,
                           department: str | None = None, status: str | None = None,
                           flagged: bool | None = None, q: str | None = None,
                           current_user: CurrentUser = Depends(require_tenant_read)):
    records = await repo.list_attendance(
        current_user.organization_id, date=date, location_id=location_id,
        department=department, status=status, flagged=flagged, q=q,
    )
    return {"items": records, "next_cursor": None}


@router.get("/reports/org-day")
async def org_day_report(date: str, current_user: CurrentUser = Depends(require_tenant_read)):
    """org_day_summary(date) (spec §4.5): per-branch counts of the five
    statuses plus a flagged count, computed on demand from attendance
    records for that date. Employees with no attendance row for the date
    are reported separately as `not_checked_in` -- v1 has no end-of-day
    batch job that auto-marks a no-show as `absent` (not specified for the
    M0-M2 slice), so that determination is left to an Admin/HR reason entry."""
    records = await repo.list_attendance(current_user.organization_id, date=date)
    employees = await repo.list_employees(current_user.organization_id)
    locations = {l["id"]: l for l in await repo.list_locations(current_user.organization_id, include_inactive=True)}

    by_location: dict[str, dict] = {}
    for loc_id, loc in locations.items():
        by_location[loc_id] = {
            "location_id": loc_id, "location_name": loc["name"],
            "on_time": 0, "late": 0, "reason": 0, "absent": 0, "off": 0, "flagged": 0,
        }

    checked_in_employee_ids = set()
    for r in records:
        checked_in_employee_ids.add(r["employee_id"])
        bucket = by_location.get(r["location_id"])
        if bucket is None:
            continue
        bucket[r["status"]] = bucket.get(r["status"], 0) + 1
        if r.get("flagged"):
            bucket["flagged"] += 1

    not_checked_in = sum(
        1 for e in employees if e.get("is_active", True) and e["id"] not in checked_in_employee_ids
    )

    return {"date": date, "branches": list(by_location.values()), "not_checked_in": not_checked_in}
