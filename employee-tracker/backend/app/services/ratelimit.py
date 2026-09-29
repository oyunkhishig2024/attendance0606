"""In-memory fixed-window rate limiter (spec §5.1: auth 10/min/IP, public
check-in 30/min/IP and 5/min/token). A single-process demo limiter; a real
multi-instance deployment would back this with Redis instead."""
import time
from collections import defaultdict

_windows: dict[str, list[float]] = defaultdict(list)


def check(key: str, *, limit: int, window_seconds: int = 60) -> bool:
    now = time.monotonic()
    bucket = _windows[key]
    cutoff = now - window_seconds
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


def reset_for_tests() -> None:
    _windows.clear()
