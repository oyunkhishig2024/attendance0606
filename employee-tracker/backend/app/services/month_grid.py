"""employee_month_grid(employee_id, month) (spec §4.5): a read-only
projection assembled from attendance plus holiday and schedule context so
`off` days are explained (rest day vs holiday) rather than appearing as
gaps, and a past day with no check-in and no reason log reads as `absent`
rather than nothing at all."""
from datetime import date as date_cls

from app import repo
from app.services.dates import days_in_month, org_local_date_str
from app.services.schedule import effective_work_days, resolve_schedule
from app.utils import utcnow


async def build_employee_month_grid(organization_id: str, employee: dict, month: str) -> list[dict]:
    org = await repo.get_organization(organization_id)
    all_dates = days_in_month(month)
    start_date, end_date = all_dates[0], all_dates[-1]

    attendance_by_date = {
        r["date"]: r for r in await repo.list_attendance_for_employee(organization_id, employee["id"],
                                                                       start_date, end_date)
    }
    holidays = {h["date"] for h in await repo.list_holidays(organization_id) if h["date"].startswith(month)}
    schedule = await resolve_schedule(organization_id, employee)
    work_days = effective_work_days(employee, schedule) if schedule else []
    today_str = org_local_date_str(utcnow(), org["timezone"])

    grid = []
    for date_str in all_dates:
        record = attendance_by_date.get(date_str)
        if record is not None:
            grid.append({
                "date": date_str, "status": record["status"], "check_in_time": record.get("check_in_time"),
                "distance_m": record.get("distance_m"), "flagged": record.get("flagged", False),
                "explanation": None,
            })
            continue

        weekday = date_cls.fromisoformat(date_str).isoweekday()
        is_holiday = date_str in holidays
        is_workday = weekday in work_days and not is_holiday

        if is_holiday:
            grid.append({"date": date_str, "status": "off", "check_in_time": None, "distance_m": None,
                         "flagged": False, "explanation": "holiday"})
        elif not is_workday:
            grid.append({"date": date_str, "status": "off", "check_in_time": None, "distance_m": None,
                         "flagged": False, "explanation": "rest_day"})
        elif date_str < today_str:
            grid.append({"date": date_str, "status": "absent", "check_in_time": None, "distance_m": None,
                         "flagged": False, "explanation": None})
        else:
            grid.append({"date": date_str, "status": None, "check_in_time": None, "distance_m": None,
                         "flagged": False, "explanation": "pending"})

    return grid
