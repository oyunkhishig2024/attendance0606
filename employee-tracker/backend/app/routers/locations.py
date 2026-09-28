from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_admin, require_tenant_read
from app.errors import AppError
from app.models import LocationCreate, LocationUpdate

router = APIRouter(prefix="/api/locations", tags=["locations"])


def _for_role(location: dict, role: str) -> dict:
    """§4.4 rule 5: Manager sees coordinates rounded to 3 decimal places
    (~110 m) -- enough to locate a branch, not to reconstruct a dwelling."""
    if role != "Manager":
        return location
    rounded = dict(location)
    rounded["latitude"] = round(location["latitude"], 3)
    rounded["longitude"] = round(location["longitude"], 3)
    return rounded


@router.get("")
async def list_locations(current_user: CurrentUser = Depends(require_tenant_read)):
    items = await repo.list_locations(current_user.organization_id, include_inactive=current_user.role == "Admin")
    return {"items": [_for_role(i, current_user.role) for i in items], "next_cursor": None}


@router.post("")
async def create_location(body: LocationCreate, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_admin)):
    location = await repo.create_location(current_user.organization_id, body.model_dump())
    await audit_write(request, current_user, "location.create", location["id"])
    return location


@router.put("/{location_id}")
async def update_location(location_id: str, body: LocationUpdate, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_admin)):
    patch = body.model_dump(exclude_unset=True)
    location = await repo.update_location(current_user.organization_id, location_id, patch)
    if location is None:
        raise AppError(404, "not_found", "Салбар олдсонгүй.")
    await audit_write(request, current_user, "location.update", location_id, patch)
    return location


@router.delete("/{location_id}")
async def delete_location(location_id: str, request: Request,
                           current_user: CurrentUser = Depends(require_tenant_admin)):
    """Soft delete (spec §4.4 rule 2): hidden from pickers; check-in against
    it is refused with code branch_inactive rather than hard-deleted."""
    location = await repo.get_location(current_user.organization_id, location_id)
    if location is None:
        raise AppError(404, "not_found", "Салбар олдсонгүй.")
    await repo.soft_delete_location(current_user.organization_id, location_id)
    await audit_write(request, current_user, "location.delete", location_id)
    return {"ok": True}
