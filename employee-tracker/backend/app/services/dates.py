from datetime import datetime
from zoneinfo import ZoneInfo


def org_local_now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def org_local_date_str(dt_utc: datetime, timezone_name: str) -> str:
    return dt_utc.astimezone(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")


def iso_weekday(dt_local: datetime) -> int:
    """1 = Monday ... 7 = Sunday, matching the spec's work_days[] convention."""
    return dt_local.isoweekday()
