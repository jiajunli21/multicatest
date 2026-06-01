import redis

from ifund_hq_project.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    REDIS_SOCKET_TIMEOUT,
    REDIS_SOCKET_CONNECT_TIMEOUT,
    RANK_DATA_KEY,
)


_pool: redis.ConnectionPool | None = None


def _get_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
            decode_responses=True,
        )
    return _pool


def get_rank_data() -> str | None:
    try:
        r = redis.Redis(connection_pool=_get_pool())
        value = r.get(RANK_DATA_KEY)
        return value
    except redis.RedisError:
        return None
