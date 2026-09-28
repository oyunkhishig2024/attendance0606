"""Dev/deploy bootstrap: there is no HTTP route that creates a SystemAdmin
(by design -- platform admin provisioning is out-of-band, spec §1.2 item 1),
so the very first one is seeded here from environment variables.

Usage: python -m app.seed
Also seeds the demo organization described in spec §12.12, which is
explicitly a development fixture and must not run against a production
database -- guarded by SEED_DEMO_DATA=true.
"""
import asyncio
import os

from app import repo
from app.db import ensure_indexes
from app.security import hash_password


async def ensure_platform_admin() -> None:
    email = os.environ.get("PLATFORM_ADMIN_EMAIL")
    password = os.environ.get("PLATFORM_ADMIN_PASSWORD")
    if not email or not password:
        print("PLATFORM_ADMIN_EMAIL / PLATFORM_ADMIN_PASSWORD not set; skipping platform admin seed.")
        return
    if await repo.get_user_by_email(email) is not None:
        print(f"Platform admin {email} already exists.")
        return
    await repo.create_user(
        organization_id=None, name="Platform Admin", email=email,
        password_hash=hash_password(password), role="SystemAdmin",
    )
    print(f"Created platform admin {email}.")


async def seed_demo_organization() -> None:
    if os.environ.get("SEED_DEMO_DATA", "").lower() != "true":
        return
    name = "Демо Групп ХХК"
    existing = await repo.list_organizations()
    if any(o["name"] == name for o in existing):
        print("Demo organization already exists.")
        return

    org = await repo.create_organization(name)
    default_schedule = await repo.create_default_schedule(org["id"])
    await repo.create_user(
        organization_id=org["id"], name="Demo Admin", email="demo-admin@example.com",
        password_hash=hash_password("password1"), role="Admin",
    )
    location = await repo.create_location(org["id"], {
        "name": "Төв салбар", "address": "Ulaanbaatar", "latitude": 47.9188, "longitude": 106.9176,
        "radius_m": 150, "start_time": "08:30", "grace_minutes": 10, "max_accuracy_m": 100,
    })
    for i in range(1, 6):
        await repo.create_employee(org["id"], {
            "full_name": f"Ажилтан {i}", "position": "Staff", "department": "Sales",
            "location_id": location["id"], "shift_template_id": default_schedule["id"],
        })
    print(f"Seeded demo organization '{name}' with 1 branch and 5 employees.")


async def main() -> None:
    await ensure_indexes()
    await ensure_platform_admin()
    await seed_demo_organization()


if __name__ == "__main__":
    asyncio.run(main())
