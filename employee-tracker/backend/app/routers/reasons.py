from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_read, require_tenant_write
from app.errors import AppError
from app.models import ReasonLogCreate
from app.reasons_catalog import REASON_CATALOG, REASON_KEYS
from app.services.dates import date_range_str

router = APIRouter(prefix="/api/reasons", tags=["reasons"])


@router.get("/catalog")
async def get_reason_catalog(current_user: CurrentUser = Depends(require_tenant_read)):
    return {"items": [{"key": k, "label": v} for k, v in REASON_CATALOG.items()]}


@router.get("")
async def list_reasons(employee_id: str | None = None, current_user: CurrentUser = Depends(require_tenant_read)):
    return {"items": await repo.list_reason_logs(current_user.organization_id, employee_id=employee_id),
            "next_cursor": None}


@router.post("")
async def create_reasons(body: ReasonLogCreate, request: Request,
                          current_user: CurrentUser = Depends(require_tenant_write)):
    if body.reason_key not in REASON_KEYS:
        raise AppError(422, "invalid_reason_key", "Тодорхойгүй шалтгааны төрөл байна.", field="reason_key")
    try:
        dates = date_range_str(body.start_date, body.end_date)
    except ValueError:
        raise AppError(422, "invalid_date_range", "Огнооны хүрээ буруу байна.", field="end_date")

    # Resolve every employee before writing anything, so an invalid id
    # partway through the list can't leave earlier employees' rows written
    # while the call as a whole reports failure to the caller.
    employees = {}
    for employee_id in body.employee_ids:
        employee = await repo.get_employee(current_user.organization_id, employee_id)
        if employee is None:
            raise AppError(422, "invalid_employee", f"Ажилтан олдсонгүй: {employee_id}", field="employee_ids")
        employees[employee_id] = employee

    created = []
    for employee_id, employee in employees.items():
        log = await repo.create_reason_log(current_user.organization_id, {
            "employee_id": employee_id, "reason_key": body.reason_key,
            "start_date": body.start_date, "end_date": body.end_date,
            "note": body.note, "created_by": current_user.id,
        })
        created.append(log)
        for date_str in dates:
            await repo.upsert_attendance_reason(
                current_user.organization_id, employee_id, employee["location_id"], date_str,
            )

    await audit_write(request, current_user, "reason.create", ",".join(body.employee_ids),
                       {"reason_key": body.reason_key, "start_date": body.start_date, "end_date": body.end_date})
    return {"items": created}
