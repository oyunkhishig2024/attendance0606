"""Data-access layer. Every tenant-scoped function takes organization_id as a
mandatory positional argument (spec §2.3 rule 2) -- there is no code path here
that reads a tenant collection without it. The only exceptions are the three
the spec itself calls out: user lookup by email (global uniqueness, needed
before an org is known at login), platform (SystemAdmin) functions, and
employee lookup by public_token (the public check-in surface resolves
organization_id FROM the token, per §2.3 rule 4)."""
from typing import Any, Optional

from app.db import db
from app.utils import new_id, new_public_token, utcnow

DEFAULT_SCHEDULE_NAME = "Стандарт"


# ---- organizations -------------------------------------------------------

async def create_organization(name: str) -> dict:
    org = {
        "id": new_id(),
        "name": name,
        "timezone": "Asia/Ulaanbaatar",
        "status": "active",
        "consent_version": "v1",
        "created_at": utcnow(),
    }
    await db.organizations.insert_one(org)
    return org


async def get_organization(organization_id: str) -> Optional[dict]:
    return await db.organizations.find_one({"id": organization_id})


async def list_organizations() -> list[dict]:
    return await db.organizations.find().to_list(length=1000)


async def set_organization_status(organization_id: str, status: str) -> Optional[dict]:
    await db.organizations.update_one({"id": organization_id}, {"$set": {"status": status}})
    return await get_organization(organization_id)


async def count_organizations_by_status() -> dict[str, int]:
    orgs = await list_organizations()
    counts = {"active": 0, "suspended": 0}
    for o in orgs:
        counts[o["status"]] = counts.get(o["status"], 0) + 1
    return counts


async def count_all_tenant_users() -> int:
    """Platform analytics reads aggregate counts only (spec §2.3 rule 3);
    it never dereferences employees or attendance rows."""
    return await db.users.count_documents({"organization_id": {"$ne": None}})


# ---- users -----------------------------------------------------------------

async def get_user_by_email(email: str) -> Optional[dict]:
    """Global by design: email uniqueness spans all tenants (spec §3.1)."""
    return await db.users.find_one({"email": email})


async def get_user_by_id(organization_id: str, user_id: str) -> Optional[dict]:
    return await db.users.find_one({"id": user_id, "organization_id": organization_id})


async def get_user_by_id_any_org(user_id: str) -> Optional[dict]:
    """Used only by auth/me and JWT resolution, keyed on the token's own sub."""
    return await db.users.find_one({"id": user_id})


async def create_user(*, organization_id: Optional[str], name: str, email: str,
                       password_hash: str, role: str, must_change_password: bool = False) -> dict:
    user = {
        "id": new_id(),
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "organization_id": organization_id,
        "must_change_password": must_change_password,
        "disabled": False,
        "last_login_at": None,
        "created_at": utcnow(),
    }
    await db.users.insert_one(user)
    return user


async def list_users(organization_id: str) -> list[dict]:
    return await db.users.find({"organization_id": organization_id}).to_list(length=1000)


async def update_user(organization_id: str, user_id: str, patch: dict) -> Optional[dict]:
    await db.users.update_one({"id": user_id, "organization_id": organization_id}, {"$set": patch})
    return await get_user_by_id(organization_id, user_id)


async def delete_user(organization_id: str, user_id: str) -> None:
    await db.users.delete_one({"id": user_id, "organization_id": organization_id})


async def touch_login(user_id: str) -> None:
    await db.users.update_one({"id": user_id}, {"$set": {"last_login_at": utcnow()}})


# ---- locations (branches) ---------------------------------------------------

async def create_location(organization_id: str, data: dict) -> dict:
    location = {
        "id": new_id(),
        "organization_id": organization_id,
        "is_active": True,
        "created_at": utcnow(),
        **data,
    }
    await db.locations.insert_one(location)
    return location


async def list_locations(organization_id: str, *, include_inactive: bool = False) -> list[dict]:
    query: dict[str, Any] = {"organization_id": organization_id}
    if not include_inactive:
        query["is_active"] = True
    return await db.locations.find(query).to_list(length=1000)


async def get_location(organization_id: str, location_id: str) -> Optional[dict]:
    return await db.locations.find_one({"id": location_id, "organization_id": organization_id})


async def update_location(organization_id: str, location_id: str, patch: dict) -> Optional[dict]:
    await db.locations.update_one({"id": location_id, "organization_id": organization_id}, {"$set": patch})
    return await get_location(organization_id, location_id)


async def soft_delete_location(organization_id: str, location_id: str) -> None:
    await db.locations.update_one(
        {"id": location_id, "organization_id": organization_id}, {"$set": {"is_active": False}}
    )


async def employee_count_for_location(organization_id: str, location_id: str) -> int:
    return await db.employees.count_documents(
        {"organization_id": organization_id, "location_id": location_id, "is_active": True}
    )


# ---- shift_templates (schedules) --------------------------------------------

async def create_default_schedule(organization_id: str) -> dict:
    return await create_shift_template(
        organization_id,
        {
            "name": DEFAULT_SCHEDULE_NAME,
            "start_time": "08:30",
            "end_time": "17:30",
            "grace_minutes": 10,
            "work_days": [1, 2, 3, 4, 5],
            "color": "#243b8f",
            "is_default": True,
            "assigned_departments": [],
            "assigned_location_ids": [],
        },
    )


async def create_shift_template(organization_id: str, data: dict) -> dict:
    shift = {
        "id": new_id(),
        "organization_id": organization_id,
        "is_active": True,
        "is_default": False,
        "created_at": utcnow(),
        **data,
    }
    await db.shift_templates.insert_one(shift)
    return shift


async def list_shift_templates(organization_id: str) -> list[dict]:
    return await db.shift_templates.find({"organization_id": organization_id}).to_list(length=1000)


async def get_shift_template(organization_id: str, shift_id: str) -> Optional[dict]:
    return await db.shift_templates.find_one({"id": shift_id, "organization_id": organization_id})


async def get_default_schedule(organization_id: str) -> Optional[dict]:
    return await db.shift_templates.find_one({"organization_id": organization_id, "is_default": True})


async def update_shift_template(organization_id: str, shift_id: str, patch: dict) -> Optional[dict]:
    await db.shift_templates.update_one({"id": shift_id, "organization_id": organization_id}, {"$set": patch})
    return await get_shift_template(organization_id, shift_id)


async def count_employees_on_schedule(organization_id: str, shift_id: str) -> int:
    return await db.employees.count_documents({"organization_id": organization_id, "shift_template_id": shift_id})


async def reassign_employees_to_default(organization_id: str, from_shift_id: str, default_id: str) -> int:
    result = await db.employees.update_many(
        {"organization_id": organization_id, "shift_template_id": from_shift_id},
        {"$set": {"shift_template_id": default_id}},
    )
    return result.modified_count


async def delete_shift_template(organization_id: str, shift_id: str) -> None:
    await db.shift_templates.delete_one({"id": shift_id, "organization_id": organization_id})


# ---- employees ---------------------------------------------------------------

async def create_employee(organization_id: str, data: dict) -> dict:
    employee = {
        "id": new_id(),
        "organization_id": organization_id,
        "public_token": new_public_token(),
        "registered_device": None,
        "consent_signed": False,
        "consent_version": None,
        "is_active": True,
        "created_at": utcnow(),
        **data,
    }
    await db.employees.insert_one(employee)
    return employee


async def list_employees(organization_id: str, *, location_id: Optional[str] = None,
                          department: Optional[str] = None) -> list[dict]:
    query: dict[str, Any] = {"organization_id": organization_id}
    if location_id:
        query["location_id"] = location_id
    if department:
        query["department"] = department
    return await db.employees.find(query).to_list(length=10000)


async def get_employee(organization_id: str, employee_id: str) -> Optional[dict]:
    return await db.employees.find_one({"id": employee_id, "organization_id": organization_id})


async def get_employee_by_token(public_token: str) -> Optional[dict]:
    """Public surface: resolves organization_id FROM the token (spec §2.3 rule 4)."""
    return await db.employees.find_one({"public_token": public_token})


async def update_employee(organization_id: str, employee_id: str, patch: dict) -> Optional[dict]:
    await db.employees.update_one({"id": employee_id, "organization_id": organization_id}, {"$set": patch})
    return await get_employee(organization_id, employee_id)


async def record_consent(employee_id: str, *, device_fingerprint_hash: str, consent_version: str) -> None:
    await db.employees.update_one(
        {"id": employee_id},
        {"$set": {
            "consent_signed": True,
            "consent_version": consent_version,
            "registered_device": device_fingerprint_hash,
        }},
    )


# ---- attendance ----------------------------------------------------------------

async def get_attendance_for_day(organization_id: str, employee_id: str, date: str) -> Optional[dict]:
    return await db.attendance.find_one(
        {"organization_id": organization_id, "employee_id": employee_id, "date": date}
    )


async def create_attendance(organization_id: str, data: dict) -> dict:
    record = {
        "id": new_id(),
        "organization_id": organization_id,
        "source": "public_link",
        "created_at": utcnow(),
        **data,
    }
    await db.attendance.insert_one(record)
    return record


async def list_attendance(organization_id: str, *, date: Optional[str] = None,
                           location_id: Optional[str] = None, department: Optional[str] = None,
                           status: Optional[str] = None, flagged: Optional[bool] = None,
                           q: Optional[str] = None) -> list[dict]:
    query: dict[str, Any] = {"organization_id": organization_id}
    if date:
        query["date"] = date
    if location_id:
        query["location_id"] = location_id
    if status:
        query["status"] = status
    if flagged is not None:
        query["flagged"] = flagged
    records = await db.attendance.find(query).sort("date", -1).to_list(length=10000)
    if department or q:
        employees = {e["id"]: e for e in await list_employees(organization_id)}
        records = [
            r for r in records
            if (not department or employees.get(r["employee_id"], {}).get("department") == department)
            and (not q or q.lower() in employees.get(r["employee_id"], {}).get("full_name", "").lower())
        ]
    return records


# ---- holidays ------------------------------------------------------------------

async def create_holiday(organization_id: str, date: str, name: str) -> dict:
    holiday = {"id": new_id(), "organization_id": organization_id, "date": date, "name": name,
               "created_at": utcnow()}
    await db.holidays.insert_one(holiday)
    return holiday


async def list_holidays(organization_id: str) -> list[dict]:
    return await db.holidays.find({"organization_id": organization_id}).to_list(length=1000)


async def get_holiday(organization_id: str, holiday_id: str) -> Optional[dict]:
    return await db.holidays.find_one({"id": holiday_id, "organization_id": organization_id})


async def is_holiday(organization_id: str, date: str) -> bool:
    return await db.holidays.find_one({"organization_id": organization_id, "date": date}) is not None


async def delete_holiday(organization_id: str, holiday_id: str) -> None:
    await db.holidays.delete_one({"id": holiday_id, "organization_id": organization_id})


# ---- audit_logs -----------------------------------------------------------------

async def write_audit_log(*, actor_user_id: str, action: str, target: str,
                           organization_id: Optional[str], metadata: dict, ip: Optional[str]) -> None:
    await db.audit_logs.insert_one({
        "id": new_id(),
        "actor_user_id": actor_user_id,
        "action": action,
        "target": target,
        "organization_id": organization_id,
        "metadata": metadata,
        "ip": ip,
        "created_at": utcnow(),
    })


async def list_audit_logs(organization_id: str) -> list[dict]:
    return await db.audit_logs.find({"organization_id": organization_id}).sort("created_at", -1).to_list(length=1000)


async def list_platform_audit_logs() -> list[dict]:
    return await db.audit_logs.find().sort("created_at", -1).to_list(length=1000)
