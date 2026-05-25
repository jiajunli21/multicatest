"""数据缓存策略。[default]

缓存层级:
- L1: 内存字典 (进程内, TTL 5分钟)
- L2: SQLite db (跨进程, 持久化)

适用数据:
- DI-001: 热度原始字段 — 缓存最近22日窗口 [mock]
- DI-002: 收盘价序列 — 缓存最近22日 [default]
- DI-003: 成交额序列 — 缓存最近20日 [default]
- DI-010: ETF综合分数 — 缓存当日结果 [default]

缓存与DB一致性策略 [default]:
- 写入时: 先写DB(事务), 后更新缓存
- 读取时: 缓存命中直接返回, 未命中从DB加载
- 淘汰: TTL过期 + 主动失效
- 缓存不可用时降级到直接读DB
"""

import time
from threading import Lock
from typing import Optional


class MemoryCache:
    """进程内内存缓存，线程安全。"""

    def __init__(self, default_ttl: int = 300):
        self._store = {}
        self._expiry = {}
        self._lock = Lock()
        self._default_ttl = default_ttl  # 5分钟

    def get(self, key: str) -> Optional[any]:
        with self._lock:
            if key in self._expiry and time.time() < self._expiry[key]:
                return self._store.get(key)
            if key in self._store:
                del self._store[key]
                del self._expiry[key]
            return None

    def set(self, key: str, value: any, ttl: int = None):
        with self._lock:
            self._store[key] = value
            self._expiry[key] = time.time() + (ttl or self._default_ttl)

    def invalidate(self, key: str = None):
        """失效缓存。key为None时清空全部。"""
        with self._lock:
            if key is None:
                self._store.clear()
                self._expiry.clear()
            elif key in self._store:
                del self._store[key]
                del self._expiry[key]


# 全局内存缓存实例
cache = MemoryCache(default_ttl=300)


def cache_key(prefix: str, etf_code: str, date: str = None) -> str:
    """生成缓存key。"""
    if date:
        return f"{prefix}:{etf_code}:{date}"
    return f"{prefix}:{etf_code}"


def get_or_set(key: str, loader, ttl: int = None) -> any:
    """缓存读取模式：命中返回，未命中从loader加载并缓存。

    Args:
        key: 缓存key
        loader: callable, 数据加载函数，缓存未命中时调用
        ttl: 过期时间(秒), None使用默认值

    Returns:
        loader返回值, loader失败返回None
    """
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        data = loader()
        if data is not None:
            cache.set(key, data, ttl)
        return data
    except Exception:
        return None
