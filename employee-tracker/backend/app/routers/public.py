from fastapi import APIRouter, Request, Response

from app import repo
from app.errors import AppError
from app.models import CheckInRequest, ConsentRequest
from app.services.checkin import perform_checkin
from app.services.dates import iso_weekday, org_local_now
from app.services.fingerprint import hash_fingerprint
from app.services.ratelimit import check as rate_limit_check
from app.services.schedule import effective_work_days, resolve_schedule
from app.utils import utcnow

router = APIRouter(prefix="/api/public", tags=["public"])

CONSENT_TEXT_MN = (
    "Таны байршлын мэдээллийг зөвхөн ажилдаа ирснийг бүртгэх зорилгоор, "
    "ирц бүртгэх мөчид авна. Байгууллага таны байршлын түүхийг тогтмол хянахгүй."
)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def _resolve_employee_or_404(token: str) -> dict:
    employee = await repo.get_employee_by_token(token)
    if employee is None or not employee.get("is_active", True):
        raise AppError(404, "not_found", "Холбоос хүчингүй байна.")
    return employee


@router.get("/employee/{token}")
async def get_public_employee(token: str, response: Response, request: Request):
    _no_store(response)
    if not rate_limit_check(f"public_ip:{_client_ip(request)}", limit=30):
        raise AppError(429, "rate_limited", "Хэт олон хүсэлт. Түр хүлээнэ үү.")

    employee = await _resolve_employee_or_404(token)
    location = await repo.get_location(employee["organization_id"], employee["location_id"])
    org = await repo.get_organization(employee["organization_id"])

    schedule = await resolve_schedule(employee["organization_id"], employee)
    shift_window = None
    if schedule and location:
        today = iso_weekday(org_local_now(org["timezone"]))
        if today in effective_work_days(employee, schedule):
            shift_window = f"{schedule['start_time']} - {schedule['end_time']}"

    return {
        "first_name": employee["full_name"].split(" ")[0],
        "branch_name": location["name"] if location else None,
        "branch_active": bool(location and location.get("is_active", True)),
        "today_shift_window": shift_window,
    }


@router.post("/checkin/{token}")
async def public_checkin(token: str, body: CheckInRequest, response: Response, request: Request):
    _no_store(response)
    ip = _client_ip(request)
    if not rate_limit_check(f"public_ip:{ip}", limit=30):
        raise AppError(429, "rate_limited", "Хэт олон хүсэлт. Түр хүлээнэ үү.")
    if not rate_limit_check(f"public_token:{token}", limit=5):
        raise AppError(429, "rate_limited", "Хэт олон хүсэлт. Түр хүлээнэ үү.")

    employee = await _resolve_employee_or_404(token)
    location = await repo.get_location(employee["organization_id"], employee["location_id"])
    if location is None or not location.get("is_active", True):
        raise AppError(409, "branch_inactive", "Энэ салбар идэвхгүй байна.")

    outcome = await perform_checkin(employee["organization_id"], employee, location, body, utcnow())
    if not outcome.ok:
        status_code = 422 if outcome.accuracy_required_retry else 409
        raise AppError(status_code, outcome.code, outcome.message)

    return {
        "status": outcome.record["status"],
        "distance_m": outcome.distance_m,
        "check_in_time": outcome.record["check_in_time"],
        "flagged": outcome.record.get("flagged", False),
    }


@router.get("/consent/{token}")
async def get_public_consent(token: str, response: Response):
    _no_store(response)
    employee = await _resolve_employee_or_404(token)
    org = await repo.get_organization(employee["organization_id"])
    return {"consent_text": CONSENT_TEXT_MN, "consent_version": org["consent_version"]}


@router.post("/consent/{token}")
async def post_public_consent(token: str, body: ConsentRequest, response: Response):
    _no_store(response)
    if not body.acknowledged:
        raise AppError(422, "consent_not_acknowledged", "Зөвшөөрлийг баталгаажуулна уу.", field="acknowledged")

    employee = await _resolve_employee_or_404(token)
    org = await repo.get_organization(employee["organization_id"])
    fingerprint_hash = hash_fingerprint(body.device_fingerprint)
    await repo.record_consent(employee["id"], device_fingerprint_hash=fingerprint_hash,
                               consent_version=org["consent_version"])
    return {"ok": True, "consent_version": org["consent_version"]}
