from app.config import settings


class _NoIdCollection:
    """Wraps a Motor/mongomock collection so callers never see Mongo's own
    `_id` (ObjectId) -- every document already carries its own UUID `id`
    (spec §4: 'application-generated string id ... rather than _id, so
    responses are stable and safe to pass around the client')."""

    def __init__(self, collection):
        self._collection = collection

    def find_one(self, filter=None, *args, **kwargs):
        kwargs.setdefault("projection", {"_id": 0})
        return self._collection.find_one(filter or {}, *args, **kwargs)

    def find(self, filter=None, *args, **kwargs):
        kwargs.setdefault("projection", {"_id": 0})
        return self._collection.find(filter or {}, *args, **kwargs)

    async def insert_one(self, document, *args, **kwargs):
        result = await self._collection.insert_one(document, *args, **kwargs)
        document.pop("_id", None)
        return result

    def __getattr__(self, name):
        return getattr(self._collection, name)


class _NoIdDatabase:
    def __init__(self, database):
        self._database = database
        self._cache: dict[str, _NoIdCollection] = {}

    def __getattr__(self, name):
        if name not in self._cache:
            self._cache[name] = _NoIdCollection(getattr(self._database, name))
        return self._cache[name]


def _build_client():
    if settings.mongo_url.startswith("mongomock://"):
        from mongomock_motor import AsyncMongoMockClient

        return AsyncMongoMockClient()
    from motor.motor_asyncio import AsyncIOMotorClient

    return AsyncIOMotorClient(settings.mongo_url)


client = _build_client()
db = _NoIdDatabase(client[settings.db_name])


async def ensure_indexes() -> None:
    await db.users.create_index("email", unique=True)
    await db.users.create_index([("organization_id", 1), ("role", 1)])
    await db.locations.create_index([("organization_id", 1), ("is_active", 1)])
    await db.shift_templates.create_index([("organization_id", 1), ("is_default", 1)])
    await db.employees.create_index("public_token", unique=True)
    await db.employees.create_index([("organization_id", 1), ("location_id", 1)])
    await db.employees.create_index([("organization_id", 1), ("department", 1)])
    await db.attendance.create_index([("organization_id", 1), ("date", -1)])
    await db.attendance.create_index([("employee_id", 1), ("date", 1)], unique=True)
    await db.attendance.create_index([("organization_id", 1), ("flagged", 1), ("date", -1)])
    await db.reason_logs.create_index([("organization_id", 1), ("employee_id", 1), ("start_date", -1)])
    await db.holidays.create_index([("organization_id", 1), ("date", 1)], unique=True)
    await db.audit_logs.create_index([("organization_id", 1), ("created_at", -1)])


def reset_db_for_tests():
    """Swap in a fresh mongomock backend, in place, so modules that already
    did `from app.db import db` keep working against the new one -- rebinding
    the module-level name here would leave those imports pointing stale."""
    global client
    from mongomock_motor import AsyncMongoMockClient

    client = AsyncMongoMockClient()
    db._database = client[settings.db_name]
    db._cache = {}
    return db
