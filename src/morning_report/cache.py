"""缓存策略模块。

Status: [default]

策略：简单内存缓存 + TTL。
- 缓存 ETF 评分结果（按日期 keyed）
- 缓存历史查询结果
- TTL: CACHE_TTL_SECONDS (默认 300s)
"""

import threading
import time
from datetime import date
from typing import Optional

from .config import CACHE_TTL_SECONDS


class SimpleCache:
    """简单线程安全缓存."""

    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS):
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[object]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            ts, val = entry
            if time.monotonic() - ts > self._ttl:
                del self._store[key]
                return None
            return val

    def set(self, key: str, value: object):
        with self._lock:
            self._store[key] = (time.monotonic(), value)

    def invalidate(self, key: Optional[str] = None):
        """失效缓存。key=None 时清空全部."""
        with self._lock:
            if key is None:
                self._store.clear()
            elif key in self._store:
                del self._store[key]

    def _make_key(self, prefix: str, calc_date: date) -> str:
        return f"{prefix}:{calc_date.isoformat()}"


# 全局缓存实例
_score_cache = SimpleCache()
_top5_cache = SimpleCache()
_history_cache = SimpleCache()


def cache_etf_scores(calc_date: date, scores):
    _score_cache.set(_score_cache._make_key("scores", calc_date), scores)


def get_cached_etf_scores(calc_date: date):
    return _score_cache.get(_score_cache._make_key("scores", calc_date))


def cache_top5(calc_date: date, top5):
    _top5_cache.set(_top5_cache._make_key("top5", calc_date), top5)


def get_cached_top5(calc_date: date):
    return _top5_cache.get(_top5_cache._make_key("top5", calc_date))


def cache_history(key: str, data):
    _history_cache.set(key, data)


def get_cached_history(key: str):
    return _history_cache.get(key)


def invalidate_date(calc_date: date):
    """失效指定日期的所有缓存."""
    _score_cache.invalidate(_score_cache._make_key("scores", calc_date))
    _top5_cache.invalidate(_top5_cache._make_key("top5", calc_date))
