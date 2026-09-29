import hashlib


def hash_fingerprint(raw_fingerprint: str) -> str:
    """The server never stores a raw device fingerprint, only its hash
    (spec §8.3): 'Store only the hash, plus non-identifying device_info'."""
    return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()
