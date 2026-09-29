from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_system_admin
from app.errors import AppError
from app.models import OrganizationProvisionRequest
from app.security import hash_password

router = APIRouter(prefix="/api/platform", tags=["platform"])


@router.get("/organizations")
async def list_organizations(current_user: CurrentUser = Depends(require_system_admin)):
    return {"items": await repo.list_organizations(), "next_cursor": None}


@router.post("/organizations")
async def provision_organization(body: OrganizationProvisionRequest, request: Request,
                                  current_user: CurrentUser = Depends(require_system_admin)):
    if await repo.get_user_by_email(body.admin_email) is not None:
        raise AppError(409, "email_taken", "Энэ имэйл хаяг бүртгэлтэй байна.", field="admin_email")
    org = await repo.create_organization(body.name)
    await repo.create_default_schedule(org["id"])
    await repo.create_user(
        organization_id=org["id"], name=body.admin_name, email=body.admin_email,
        password_hash=hash_password(body.admin_password), role="Admin", must_change_password=True,
    )
    await audit_write(request, current_user, "platform.organization.create", org["id"])
    return org


@router.patch("/organizations/{organization_id}/suspend")
async def suspend_organization(organization_id: str, request: Request,
                                current_user: CurrentUser = Depends(require_system_admin)):
    org = await repo.set_organization_status(organization_id, "suspended")
    if org is None:
        raise AppError(404, "not_found", "Байгууллага олдсонгүй.")
    await audit_write(request, current_user, "platform.organization.suspend", organization_id)
    return org


@router.patch("/organizations/{organization_id}/reactivate")
async def reactivate_organization(organization_id: str, request: Request,
                                   current_user: CurrentUser = Depends(require_system_admin)):
    org = await repo.set_organization_status(organization_id, "active")
    if org is None:
        raise AppError(404, "not_found", "Байгууллага олдсонгүй.")
    await audit_write(request, current_user, "platform.organization.reactivate", organization_id)
    return org


@router.get("/analytics")
async def platform_analytics(current_user: CurrentUser = Depends(require_system_admin)):
    """Aggregate counts and organization metadata only (spec §2.3 rule 3
    and §6.2 rule 3): never employees or attendance rows."""
    org_counts = await repo.count_organizations_by_status()
    return {
        "organizations_active": org_counts.get("active", 0),
        "organizations_suspended": org_counts.get("suspended", 0),
        "tenant_users_total": await repo.count_all_tenant_users(),
    }


@router.get("/audit-logs")
async def platform_audit_logs(current_user: CurrentUser = Depends(require_system_admin)):
    return {"items": await repo.list_platform_audit_logs(), "next_cursor": None}
