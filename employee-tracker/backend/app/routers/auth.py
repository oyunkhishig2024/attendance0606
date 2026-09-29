from fastapi import APIRouter, Depends, Request

from app import repo
from app.deps import CurrentUser, get_current_user
from app.errors import AppError
from app.models import ChangePasswordRequest, DeleteAccountRequest, LoginRequest, SignupRequest
from app.security import create_access_token, hash_password, verify_password
from app.services.ratelimit import check as rate_limit_check

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_public(user: dict) -> dict:
    return {
        "id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"],
        "organization_id": user.get("organization_id"),
        "must_change_password": user.get("must_change_password", False),
    }


@router.post("/signup")
async def signup(body: SignupRequest, request: Request):
    if not rate_limit_check(f"auth:{request.client.host if request.client else 'unknown'}", limit=10):
        raise AppError(429, "rate_limited", "Хэт олон оролдлого. Түр хүлээнэ үү.")

    existing = await repo.get_user_by_email(body.email)
    if existing is not None:
        raise AppError(409, "email_taken", "Энэ имэйл хаяг бүртгэлтэй байна.", field="email")

    org = await repo.create_organization(body.organization_name)
    await repo.create_default_schedule(org["id"])
    user = await repo.create_user(
        organization_id=org["id"], name=body.admin_name, email=body.email,
        password_hash=hash_password(body.password), role="Admin",
    )
    token = create_access_token(sub=user["id"], role=user["role"], org=user["organization_id"])
    return {"token": token, "user": _user_public(user), "organization": {"id": org["id"], "name": org["name"]}}


@router.post("/login")
async def login(body: LoginRequest, request: Request):
    if not rate_limit_check(f"auth:{request.client.host if request.client else 'unknown'}", limit=10):
        raise AppError(429, "rate_limited", "Хэт олон оролдлого. Түр хүлээнэ үү.")

    user = await repo.get_user_by_email(body.email)
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise AppError(401, "invalid_credentials", "Имэйл эсвэл нууц үг буруу байна.")

    if user.get("disabled"):
        raise AppError(403, "account_disabled", "Хэрэглэгчийн эрх хаагдсан байна.")

    if user.get("organization_id"):
        org = await repo.get_organization(user["organization_id"])
        if org and org["status"] == "suspended":
            raise AppError(402, "organization_suspended", "Байгууллагын эрх түдгэлзсэн байна.")

    await repo.touch_login(user["id"])
    token = create_access_token(sub=user["id"], role=user["role"], org=user.get("organization_id"))
    return {"token": token, "user": _user_public(user)}


@router.get("/me")
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "id": current_user.id, "name": current_user.name, "email": current_user.email,
        "role": current_user.role, "organization_id": current_user.organization_id,
        "must_change_password": current_user.must_change_password,
    }


@router.post("/change-password")
async def change_password(body: ChangePasswordRequest, current_user: CurrentUser = Depends(get_current_user)):
    user = await repo.get_user_by_id_any_org(current_user.id)
    if not verify_password(body.current_password, user["password_hash"]):
        raise AppError(400, "invalid_credentials", "Одоогийн нууц үг буруу байна.")
    if current_user.organization_id:
        await repo.update_user(current_user.organization_id, current_user.id, {
            "password_hash": hash_password(body.new_password), "must_change_password": False,
        })
    return {"ok": True}


@router.post("/delete-account")
async def delete_account(body: DeleteAccountRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Apple App Store compliance path (spec §6.6): self-service, requires
    password re-entry."""
    user = await repo.get_user_by_id_any_org(current_user.id)
    if not verify_password(body.password, user["password_hash"]):
        raise AppError(400, "invalid_credentials", "Нууц үг буруу байна.")
    if current_user.organization_id:
        await repo.delete_user(current_user.organization_id, current_user.id)
    return {"ok": True}
