from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Raised anywhere in the app; rendered into the spec's error shape
    (spec §5.1): { detail, code, field }. `code` is the stable string the
    client switches on; `detail` is safe to display."""

    def __init__(self, status_code: int, code: str, detail: str, field: Optional[str] = None):
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.field = field


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    body = {"detail": exc.detail, "code": exc.code}
    if exc.field:
        body["field"] = exc.field
    return JSONResponse(status_code=exc.status_code, content=body)
