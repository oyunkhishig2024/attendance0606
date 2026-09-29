import secrets
import uuid
from datetime import datetime, timezone


def new_id() -> str:
    return str(uuid.uuid4())


def new_public_token() -> str:
    return secrets.token_urlsafe(32)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
