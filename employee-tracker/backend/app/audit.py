"""audit_write: fires after any mutating handler for Admin/HR/SystemAdmin
(spec §5.8). Read handlers are not audited, to keep write amplification low."""
from typing import Optional

from fastapi import Request

from app import repo
from app.deps import CurrentUser


async def audit_write(request: Request, actor: CurrentUser, action: str, target: str,
                       metadata: Optional[dict] = None) -> None:
    if actor.role not in ("Admin", "HR", "SystemAdmin"):
        return
    await repo.write_audit_log(
        actor_user_id=actor.id,
        action=action,
        target=target,
        organization_id=actor.organization_id,
        metadata=metadata or {},
        ip=request.client.host if request.client else None,
    )
