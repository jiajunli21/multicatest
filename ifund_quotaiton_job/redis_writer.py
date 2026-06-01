"""Redis 写入层。

写入唯一 Redis key: plateStatEtf:rank:data
包含 8 份榜单 JSON + updateTime。
"""

import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Redis 客户端使用延迟导入，方便测试时替换
_redis_client = None


def _get_redis():
    """获取 Redis 连接（延迟初始化）。"""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        import redis as redis_lib

        from . import config

        _redis_client = redis_lib.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )
        _redis_client.ping()
        logger.info("Redis connected: %s:%s", config.REDIS_HOST, config.REDIS_PORT)
    except ImportError:
        logger.warning("redis-py not installed, using in-memory fallback")
        _redis_client = _InMemoryRedis()
    except Exception as e:
        logger.warning("Redis connection failed, using in-memory fallback: %s", e)
        _redis_client = _InMemoryRedis()

    return _redis_client


class _InMemoryRedis:
    """内存 Redis 模拟，用于无 redis-py 时的测试和流程验证。"""

    def __init__(self):
        self._data = {}

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None):
        self._data[key] = value
        return True

    def ping(self):
        return True

    def last_write_time(self, key: str) -> Optional[float]:
        return None


def write_rank_data(rankings: dict[str, list[dict]]) -> bool:
    """将 8 份榜单 JSON 写入 Redis key plateStatEtf:rank:data。

    Args:
        rankings: calculate_rankings() 的输出，8 份榜单 dict

    Returns:
        True=写入成功，False=写入失败
    """
    from . import config

    r = _get_redis()
    now = int(time.time())

    payload = {
        "updateTime": now,
        "changeRatioTop9": rankings.get("changeRatioTop9", []),
        "changeRatioBottom9": rankings.get("changeRatioBottom9", []),
        "speedRatioTop9": rankings.get("speedRatioTop9", []),
        "speedRatioBottom9": rankings.get("speedRatioBottom9", []),
        "volumeRatioTop9": rankings.get("volumeRatioTop9", []),
        "volumeRatioBottom9": rankings.get("volumeRatioBottom9", []),
        "limitUpCountTop9": rankings.get("limitUpCountTop9", []),
        "limitUpCountBottom9": rankings.get("limitUpCountBottom9", []),
    }

    try:
        json_str = json.dumps(payload, ensure_ascii=False)
        r.set(config.REDIS_KEY, json_str)
        logger.info("Redis write success: key=%s, updateTime=%s", config.REDIS_KEY, now)
        return True
    except Exception as e:
        logger.error("Redis write failed: %s", e)
        return False


def read_rank_data() -> Optional[dict]:
    """从 Redis 读取当前榜单数据（用于降级判断）。

    Returns:
        dict 或 None（Redis 中无数据）
    """
    from . import config

    r = _get_redis()
    try:
        raw = r.get(config.REDIS_KEY)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning("Redis read failed: %s", e)
        return None
