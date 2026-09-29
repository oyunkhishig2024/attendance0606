from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_read, require_tenant_write
from app.errors import AppError
from app.models import EmployeeCreate, EmployeeUpdate
from app.services.month_grid import build_employee_month_grid

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("")
async def list_employees(location_id: str | None = None, department: str | None = None,
                          current_user: CurrentUser = Depends(require_tenant_read)):
    items = await repo.list_employees(current_user.organization_id, location_id=location_id, department=department)
    return {"items": items, "next_cursor": None}


@router.post("")
async def create_employee(body: EmployeeCreate, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_write)):
    location = await repo.get_location(current_user.organization_id, body.location_id)
    if location is None:
        raise AppError(422, "invalid_location", "Салбар олдсонгүй.", field="location_id")
    employee = await repo.create_employee(current_user.organization_id, body.model_dump())
    await audit_write(request, current_user, "employee.create", employee["id"])
    return employee


@router.get("/{employee_id}")
async def get_employee(employee_id: str, current_user: CurrentUser = Depends(require_tenant_read)):
    employee = await repo.get_employee(current_user.organization_id, employee_id)
    if employee is None:
        raise AppError(404, "not_found", "Ажилтан олдсонгүй.")
    return employee


@router.get("/{employee_id}/month-grid")
async def get_employee_month_grid(employee_id: str, month: str,
                                   current_user: CurrentUser = Depends(require_tenant_read)):
    employee = await repo.get_employee(current_user.organization_id, employee_id)
    if employee is None:
        raise AppError(404, "not_found", "Ажилтан олдсонгүй.")
    return {"employee_id": employee_id, "month": month,
            "days": await build_employee_month_grid(current_user.organization_id, employee, month)}


@router.put("/{employee_id}")
async def update_employee(employee_id: str, body: EmployeeUpdate, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_write)):
    patch = body.model_dump(exclude_unset=True)
    employee = await repo.update_employee(current_user.organization_id, employee_id, patch)
    if employee is None:
        raise AppError(404, "not_found", "Ажилтан олдсонгүй.")
    await audit_write(request, current_user, "employee.update", employee_id, patch)
    return employee


@router.delete("/{employee_id}")
async def delete_employee(employee_id: str, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_write)):
    employee = await repo.update_employee(current_user.organization_id, employee_id, {"is_active": False})
    if employee is None:
        raise AppError(404, "not_found", "Ажилтан олдсонгүй.")
    await audit_write(request, current_user, "employee.delete", employee_id)
    return {"ok": True}
