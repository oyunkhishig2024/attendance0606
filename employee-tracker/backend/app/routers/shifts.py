from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_read, require_tenant_write
from app.errors import AppError
from app.models import ShiftTemplateCreate, ShiftTemplateUpdate

router = APIRouter(prefix="/api/shifts", tags=["shifts"])


@router.get("")
async def list_shifts(current_user: CurrentUser = Depends(require_tenant_read)):
    return {"items": await repo.list_shift_templates(current_user.organization_id), "next_cursor": None}


@router.post("")
async def create_shift(body: ShiftTemplateCreate, request: Request,
                        current_user: CurrentUser = Depends(require_tenant_write)):
    shift = await repo.create_shift_template(current_user.organization_id, body.model_dump())
    await audit_write(request, current_user, "shift.create", shift["id"])
    return shift


@router.put("/{shift_id}")
async def update_shift(shift_id: str, body: ShiftTemplateUpdate, request: Request,
                        current_user: CurrentUser = Depends(require_tenant_write)):
    shift = await repo.get_shift_template(current_user.organization_id, shift_id)
    if shift is None:
        raise AppError(404, "not_found", "Хуваарь олдсонгүй.")
    if shift.get("is_default") and current_user.role != "Admin":
        # §2.2: "Organization default schedule" capability is Admin-only (HR: denied).
        raise AppError(403, "forbidden", "Үндсэн хуваарийг зөвхөн админ засах боломжтой.")
    patch = body.model_dump(exclude_unset=True)
    updated = await repo.update_shift_template(current_user.organization_id, shift_id, patch)
    await audit_write(request, current_user, "shift.update", shift_id, patch)
    return updated


@router.patch("/{shift_id}/active")
async def toggle_shift_active(shift_id: str, is_active: bool, request: Request,
                               current_user: CurrentUser = Depends(require_tenant_write)):
    shift = await repo.get_shift_template(current_user.organization_id, shift_id)
    if shift is None:
        raise AppError(404, "not_found", "Хуваарь олдсонгүй.")

    affected = 0
    fallback_id = None
    if not is_active and not shift.get("is_default"):
        default = await repo.get_default_schedule(current_user.organization_id)
        fallback_id = default["id"] if default else None
        affected = await repo.count_employees_on_schedule(current_user.organization_id, shift_id)
        if fallback_id:
            await repo.reassign_employees_to_default(current_user.organization_id, shift_id, fallback_id)

    await repo.update_shift_template(current_user.organization_id, shift_id, {"is_active": is_active})
    await audit_write(request, current_user, "shift.toggle_active", shift_id, {"is_active": is_active})
    return {"affected_employees": affected, "fallback": fallback_id}


@router.delete("/{shift_id}")
async def delete_shift(shift_id: str, request: Request, current_user: CurrentUser = Depends(require_tenant_write)):
    shift = await repo.get_shift_template(current_user.organization_id, shift_id)
    if shift is None:
        raise AppError(404, "not_found", "Хуваарь олдсонгүй.")
    if shift.get("is_default"):
        raise AppError(409, "default_schedule_protected", "Үндсэн хуваарийг устгах боломжгүй.")

    default = await repo.get_default_schedule(current_user.organization_id)
    if default:
        await repo.reassign_employees_to_default(current_user.organization_id, shift_id, default["id"])
    await repo.delete_shift_template(current_user.organization_id, shift_id)
    await audit_write(request, current_user, "shift.delete", shift_id)
    return {"ok": True}
