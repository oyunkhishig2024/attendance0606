from fastapi import APIRouter, Depends, Request

from app import repo
from app.audit import audit_write
from app.deps import CurrentUser, require_tenant_admin, require_tenant_read
from app.errors import AppError
from app.models import UserCreate, UserUpdate
from app.security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


def _public(u: dict) -> dict:
    return {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"],
            "disabled": u.get("disabled", False), "must_change_password": u.get("must_change_password", False)}


@router.get("")
async def list_users(current_user: CurrentUser = Depends(require_tenant_read)):
    users = await repo.list_users(current_user.organization_id)
    return {"items": [_public(u) for u in users], "next_cursor": None}


@router.post("")
async def create_user(body: UserCreate, request: Request, current_user: CurrentUser = Depends(require_tenant_admin)):
    if await repo.get_user_by_email(body.email) is not None:
        raise AppError(409, "email_taken", "Энэ имэйл хаяг бүртгэлтэй байна.", field="email")
    user = await repo.create_user(
        organization_id=current_user.organization_id, name=body.name, email=body.email,
        password_hash=hash_password(body.password), role=body.role, must_change_password=True,
    )
    await audit_write(request, current_user, "user.create", user["id"])
    return _public(user)


@router.put("/{user_id}")
async def update_user(user_id: str, body: UserUpdate, request: Request,
                       current_user: CurrentUser = Depends(require_tenant_admin)):
    patch = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    user = await repo.update_user(current_user.organization_id, user_id, patch)
    if user is None:
        raise AppError(404, "not_found", "Хэрэглэгч олдсонгүй.")
    await audit_write(request, current_user, "user.update", user_id, patch)
    return _public(user)


@router.delete("/{user_id}")
async def delete_user(user_id: str, request: Request, current_user: CurrentUser = Depends(require_tenant_admin)):
    if await repo.get_user_by_id(current_user.organization_id, user_id) is None:
        raise AppError(404, "not_found", "Хэрэглэгч олдсонгүй.")
    await repo.delete_user(current_user.organization_id, user_id)
    await audit_write(request, current_user, "user.delete", user_id)
    return {"ok": True}
