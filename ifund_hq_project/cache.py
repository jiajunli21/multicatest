import threading
from cachetools import TTLCache

from ifund_hq_project.config import CAFFEINE_TTL_SECONDS


_cache_lock = threading.Lock()

_local_cache = TTLCache(maxsize=1, ttl=CAFFEINE_TTL_SECONDS)

CACHE_KEY = "plateStatEtf:rank:data"


def get_from_local() -> str | None:
    with _cache_lock:
        return _local_cache.get(CACHE_KEY)


def put_to_local(value: str) -> None:
    with _cache_lock:
        _local_cache[CACHE_KEY] = value


def invalidate_local() -> None:
    with _cache_lock:
        _local_cache.pop(CACHE_KEY, None)
