from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_read, require_tenant_write
from app.errors import AppError
from app.models import HolidayCreate

router = APIRouter(prefix="/api/holidays", tags=["holidays"])


@router.get("")
async def list_holidays(current_user: CurrentUser = Depends(require_tenant_read)):
    return {"items": await repo.list_holidays(current_user.organization_id), "next_cursor": None}


@router.post("")
async def create_holiday(body: HolidayCreate, request: Request,
                          current_user: CurrentUser = Depends(require_tenant_write)):
    holiday = await repo.create_holiday(current_user.organization_id, body.date, body.name)
    await audit_write(request, current_user, "holiday.create", holiday["id"])
    return holiday


@router.delete("/{holiday_id}")
async def delete_holiday(holiday_id: str, request: Request,
                          current_user: CurrentUser = Depends(require_tenant_write)):
    if await repo.get_holiday(current_user.organization_id, holiday_id) is None:
        raise AppError(404, "not_found", "Амралтын өдөр олдсонгүй.")
    await repo.delete_holiday(current_user.organization_id, holiday_id)
    await audit_write(request, current_user, "holiday.delete", holiday_id)
    return {"ok": True}
