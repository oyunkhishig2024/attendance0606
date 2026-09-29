from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def org_local_now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def org_local_date_str(dt_utc: datetime, timezone_name: str) -> str:
    return dt_utc.astimezone(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")


def iso_weekday(dt_local: datetime) -> int:
    """1 = Monday ... 7 = Sunday, matching the spec's work_days[] convention."""
    return dt_local.isoweekday()


def date_range_str(start_date: str, end_date: str) -> list[str]:
    """Inclusive list of YYYY-MM-DD strings from start_date to end_date."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date must not be before start_date")
    return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]


def days_in_month(month: str) -> list[str]:
    """All YYYY-MM-DD strings in a "YYYY-MM" month."""
    year, mon = map(int, month.split("-"))
    start = date(year, mon, 1)
    next_month = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return [(start + timedelta(days=i)).isoformat() for i in range((next_month - start).days)]
