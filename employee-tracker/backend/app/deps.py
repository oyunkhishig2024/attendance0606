"""Auth, role_gate, and tenant_scope links of the middleware chain (spec
§5.8): request_id -> CORS -> rate_limit -> auth -> role_gate -> tenant_scope
-> handler -> audit_write. request_id/CORS/rate_limit are wired in main.py;
this module covers auth resolution and the deny-by-default role gate."""
from dataclasses import dataclass
from typing import Optional

import jwt
from fastapi import Depends, Header, Request

from app import repo
from app.errors import AppError
from app.security import decode_access_token

PASSWORD_CHANGE_EXEMPT_PATHS = {"/api/auth/change-password", "/api/auth/me"}


@dataclass
class CurrentUser:
    id: str
    role: str
    organization_id: Optional[str]
    name: str
    email: str
    disabled: bool
    must_change_password: bool


async def get_current_user(request: Request, authorization: Optional[str] = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(401, "unauthenticated", "Нэвтрэх шаардлагатай.")
    token = authorization.split(" ", 1)[1]
    try:
        claims = decode_access_token(token)
    except jwt.PyJWTError:
        raise AppError(401, "invalid_token", "Токен хүчингүй байна.")

    user = await repo.get_user_by_id_any_org(claims["sub"])
    if user is None:
        raise AppError(401, "invalid_token", "Токен хүчингүй байна.")

    if user.get("disabled"):
        raise AppError(403, "account_disabled", "Хэрэглэгчийн эрх хаагдсан байна.")

    if user.get("organization_id"):
        org = await repo.get_organization(user["organization_id"])
        if org and org["status"] == "suspended":
            raise AppError(402, "organization_suspended", "Байгууллагын эрх түдгэлзсэн байна.")

    if user.get("must_change_password") and request.url.path not in PASSWORD_CHANGE_EXEMPT_PATHS:
        raise AppError(403, "password_change_required", "Нууц үгээ солих шаардлагатай.")

    return CurrentUser(
        id=user["id"], role=user["role"], organization_id=user.get("organization_id"),
        name=user["name"], email=user["email"], disabled=user.get("disabled", False),
        must_change_password=user.get("must_change_password", False),
    )


def require_roles(*roles: str):
    """Deny-by-default role gate (spec §2.3 rule 5): a route with no
    declared role list has no way to be reached, and role is checked before
    tenancy is even considered (rule 1)."""

    async def _dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in roles:
            raise AppError(403, "forbidden", "Энэ үйлдлийг хийх эрхгүй байна.")
        return current_user

    return _dependency


require_tenant_admin = require_roles("Admin")
require_tenant_write = require_roles("Admin", "HR")
require_tenant_read = require_roles("Admin", "HR", "Manager")
require_system_admin = require_roles("SystemAdmin")
require_any_authenticated = require_roles("SystemAdmin", "Admin", "HR", "Manager")
