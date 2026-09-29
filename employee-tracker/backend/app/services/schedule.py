"""Schedule resolution hierarchy (spec §3.4): Employee -> Department -> Branch
-> Org default. The first non-empty match wins, and resolution is computed
live at check-in time so a schedule change applies without data migration."""
from typing import Optional

from app import repo


async def resolve_schedule(organization_id: str, employee: dict) -> Optional[dict]:
    templates = await repo.list_shift_templates(organization_id)
    active = {t["id"]: t for t in templates if t.get("is_active")}

    shift_id = employee.get("shift_template_id")
    if shift_id and shift_id in active:
        return active[shift_id]

    department = employee.get("department")
    if department:
        for t in active.values():
            if department in (t.get("assigned_departments") or []):
                return t

    location_id = employee.get("location_id")
    if location_id:
        for t in active.values():
            if location_id in (t.get("assigned_location_ids") or []):
                return t

    for t in active.values():
        if t.get("is_default"):
            return t
    return None


def effective_work_days(employee: dict, schedule: dict) -> list[int]:
    """A per-employee work_days override, if set, wins over the schedule's
    own days (spec §4.1 employees.work_days[])."""
    return employee.get("work_days") or schedule.get("work_days") or []
